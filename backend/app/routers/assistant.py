from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.get("/advice")
def get_financial_advice(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    income_total = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "income",
    ).scalar()

    expense_total = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "expense",
    ).scalar()

    balance = income_total - expense_total

    advice = []

    if income_total == 0 and expense_total == 0:
        advice.append({
            "type": "info",
            "title": "Недостаточно данных",
            "message": "Добавьте доходы и расходы, чтобы система смогла сформировать персональные рекомендации."
        })
        return {
            "income_total": income_total,
            "expense_total": expense_total,
            "balance": balance,
            "advice": advice,
        }

    if expense_total > income_total:
        advice.append({
            "type": "warning",
            "title": "Расходы превышают доходы",
            "message": "За выбранный период расходы превышают доходы. Рекомендуется сократить необязательные траты и пересмотреть лимиты по категориям."
        })
    else:
        advice.append({
            "type": "success",
            "title": "Бюджет находится под контролем",
            "message": "Доходы превышают расходы. Часть свободных средств можно направить на финансовые цели или резерв."
        })

    top_expense = db.query(
        models.Category.name,
        func.coalesce(func.sum(models.Transaction.amount), 0).label("total"),
    ).join(
        models.Transaction,
        models.Transaction.category_id == models.Category.id,
    ).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "expense",
    ).group_by(
        models.Category.name,
    ).order_by(
        func.sum(models.Transaction.amount).desc(),
    ).first()

    if top_expense and expense_total > 0:
        category_name, category_total = top_expense
        share = round((category_total / expense_total) * 100, 2)

        if share >= 40:
            advice.append({
                "type": "warning",
                "title": "Высокая доля расходов в одной категории",
                "message": f"На категорию «{category_name}» приходится {share}% всех расходов. Рекомендуется проверить, можно ли снизить траты в этой категории."
            })
        else:
            advice.append({
                "type": "info",
                "title": "Расходы распределены относительно равномерно",
                "message": f"Самая крупная категория расходов — «{category_name}», её доля составляет {share}%."
            })

    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).all()

    for goal in goals:
        if goal.target_amount > 0:
            progress = round((goal.current_amount / goal.target_amount) * 100, 2)

            if progress >= 100:
                advice.append({
                    "type": "success",
                    "title": f"Цель «{goal.title}» достигнута",
                    "message": f"Вы накопили {goal.current_amount} {goal.currency}. Цель выполнена."
                })
            elif progress < 30:
                advice.append({
                    "type": "info",
                    "title": f"Низкий прогресс по цели «{goal.title}»",
                    "message": f"Текущий прогресс составляет {progress}%. Рекомендуется регулярно откладывать часть свободного остатка."
                })
            else:
                advice.append({
                    "type": "info",
                    "title": f"Прогресс по цели «{goal.title}»",
                    "message": f"Текущий прогресс составляет {progress}%. Продолжайте пополнять цель для достижения результата."
                })

    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": balance,
        "advice": advice,
    }