from typing import Optional
from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app import models
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/statistics", tags=["Statistics"])


def apply_date_filter(query, date_from: Optional[date], date_to: Optional[date]):
    if date_from:
        query = query.filter(
            models.Transaction.date >= datetime.combine(date_from, time.min)
        )

    if date_to:
        query = query.filter(
            models.Transaction.date <= datetime.combine(date_to, time.max)
        )

    return query


@router.get("/summary")
def get_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    income_query = db.query(
        func.coalesce(func.sum(models.Transaction.amount), 0)
    ).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "income",
    )
    income_total = apply_date_filter(income_query, date_from, date_to).scalar()

    expense_query = db.query(
        func.coalesce(func.sum(models.Transaction.amount), 0)
    ).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "expense",
    )
    expense_total = apply_date_filter(expense_query, date_from, date_to).scalar()

    savings_query = db.query(
        func.coalesce(func.sum(models.GoalContribution.amount), 0)
    ).filter(
        models.GoalContribution.user_id == current_user.id,
    )

    if date_from:
        savings_query = savings_query.filter(
            models.GoalContribution.date >= datetime.combine(date_from, time.min)
        )

    if date_to:
        savings_query = savings_query.filter(
            models.GoalContribution.date <= datetime.combine(date_to, time.max)
        )

    savings_total = savings_query.scalar()

    balance = income_total - expense_total
    free_balance = income_total - expense_total - savings_total

    expenses_query = db.query(
        models.Category.name,
        models.Category.color,
        func.coalesce(func.sum(models.Transaction.amount), 0).label("total"),
    ).join(
        models.Transaction,
        models.Transaction.category_id == models.Category.id,
    ).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "expense",
    )

    expenses_by_category = apply_date_filter(
        expenses_query, date_from, date_to
    ).group_by(
        models.Category.name,
        models.Category.color,
    ).order_by(
        func.sum(models.Transaction.amount).desc(),
    ).all()

    income_category_query = db.query(
        models.Category.name,
        models.Category.color,
        func.coalesce(func.sum(models.Transaction.amount), 0).label("total"),
    ).join(
        models.Transaction,
        models.Transaction.category_id == models.Category.id,
    ).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.type == "income",
    )

    income_by_category = apply_date_filter(
        income_category_query, date_from, date_to
    ).group_by(
        models.Category.name,
        models.Category.color,
    ).order_by(
        func.sum(models.Transaction.amount).desc(),
    ).all()

    return {
        "date_from": date_from,
        "date_to": date_to,
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": balance,
        "savings_total": savings_total,
        "free_balance": free_balance,
        "expenses_by_category": [
            {"category": name, "color": color, "total": total}
            for name, color, total in expenses_by_category
        ],
        "income_by_category": [
            {"category": name, "color": color, "total": total}
            for name, color, total in income_by_category
        ],
    }


@router.get("/dynamics")
def get_dynamics(
    group_by: str = "month",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if group_by not in ["day", "week", "month", "year"]:
        raise HTTPException(status_code=400, detail="group_by must be day, week, month or year")

    if group_by == "day":
        transaction_period = func.date_format(models.Transaction.date, "%Y-%m-%d")
        saving_period = func.date_format(models.GoalContribution.date, "%Y-%m-%d")
    elif group_by == "week":
        transaction_period = func.date_format(models.Transaction.date, "%x-W%v")
        saving_period = func.date_format(models.GoalContribution.date, "%x-W%v")
    elif group_by == "month":
        transaction_period = func.date_format(models.Transaction.date, "%Y-%m")
        saving_period = func.date_format(models.GoalContribution.date, "%Y-%m")
    else:
        transaction_period = func.date_format(models.Transaction.date, "%Y")
        saving_period = func.date_format(models.GoalContribution.date, "%Y")

    transactions_query = db.query(
        transaction_period.label("period"),
        func.coalesce(
            func.sum(
                case(
                    (models.Transaction.type == "income", models.Transaction.amount),
                    else_=0,
                )
            ),
            0,
        ).label("income"),
        func.coalesce(
            func.sum(
                case(
                    (models.Transaction.type == "expense", models.Transaction.amount),
                    else_=0,
                )
            ),
            0,
        ).label("expense"),
    ).filter(
        models.Transaction.user_id == current_user.id
    )

    transactions_query = apply_date_filter(transactions_query, date_from, date_to)

    transaction_rows = transactions_query.group_by("period").all()

    savings_query = db.query(
        saving_period.label("period"),
        func.coalesce(func.sum(models.GoalContribution.amount), 0).label("savings"),
    ).filter(
        models.GoalContribution.user_id == current_user.id
    )

    if date_from:
        savings_query = savings_query.filter(
            models.GoalContribution.date >= datetime.combine(date_from, time.min)
        )

    if date_to:
        savings_query = savings_query.filter(
            models.GoalContribution.date <= datetime.combine(date_to, time.max)
        )

    saving_rows = savings_query.group_by("period").all()

    result = {}

    for row in transaction_rows:
        result[row.period] = {
            "period": row.period,
            "income": float(row.income),
            "expense": float(row.expense),
            "savings": 0,
            "profit": float(row.income) - float(row.expense),
            "loss": 0,
        }

    for row in saving_rows:
        if row.period not in result:
            result[row.period] = {
                "period": row.period,
                "income": 0,
                "expense": 0,
                "savings": 0,
                "profit": 0,
                "loss": 0,
            }

        result[row.period]["savings"] = float(row.savings)

    for period_key in result:
        item = result[period_key]
        free_balance = item["income"] - item["expense"] - item["savings"]

        item["profit"] = free_balance if free_balance > 0 else 0
        item["loss"] = abs(free_balance) if free_balance < 0 else 0

    return sorted(result.values(), key=lambda item: item["period"])