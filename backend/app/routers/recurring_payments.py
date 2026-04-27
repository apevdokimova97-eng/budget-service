from datetime import date
import calendar

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/recurring-payments", tags=["Recurring payments"])


def get_payment_date(today: date, payment_day: int) -> date:
    last_day = calendar.monthrange(today.year, today.month)[1]
    real_day = min(payment_day, last_day)
    return date(today.year, today.month, real_day)


@router.post("/", response_model=schemas.RecurringPaymentResponse)
def create_recurring_payment(
    payment: schemas.RecurringPaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than 0")

    category = db.query(models.Category).filter(
        models.Category.id == payment.category_id,
        models.Category.user_id == current_user.id,
        models.Category.type == "expense",
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Expense category not found")

    new_payment = models.RecurringPayment(
        user_id=current_user.id,
        category_id=payment.category_id,
        title=payment.title,
        amount=payment.amount,
        currency=payment.currency,
        payment_day=payment.payment_day,
        reminder_days="3,1,0",
        is_active=1,
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


@router.get("/", response_model=list[schemas.RecurringPaymentResponse])
def get_recurring_payments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.RecurringPayment).filter(
        models.RecurringPayment.user_id == current_user.id
    ).order_by(models.RecurringPayment.payment_day.asc()).all()


@router.put("/{payment_id}", response_model=schemas.RecurringPaymentResponse)
def update_recurring_payment(
    payment_id: int,
    payment_data: schemas.RecurringPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    payment = db.query(models.RecurringPayment).filter(
        models.RecurringPayment.id == payment_id,
        models.RecurringPayment.user_id == current_user.id,
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Recurring payment not found")

    update_data = payment_data.model_dump(exclude_unset=True)

    if "amount" in update_data and update_data["amount"] <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than 0")

    if "category_id" in update_data:
        category = db.query(models.Category).filter(
            models.Category.id == update_data["category_id"],
            models.Category.user_id == current_user.id,
            models.Category.type == "expense",
        ).first()

        if not category:
            raise HTTPException(status_code=404, detail="Expense category not found")

    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return payment


@router.delete("/{payment_id}")
def delete_recurring_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    payment = db.query(models.RecurringPayment).filter(
        models.RecurringPayment.id == payment_id,
        models.RecurringPayment.user_id == current_user.id,
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Recurring payment not found")

    db.delete(payment)
    db.commit()

    return {"message": "Recurring payment deleted"}


@router.get("/reminders")
def get_recurring_payment_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    current_month = today.strftime("%Y-%m")
    reminders = []

    payments = db.query(models.RecurringPayment).filter(
        models.RecurringPayment.user_id == current_user.id,
        models.RecurringPayment.is_active == 1,
    ).all()

    for payment in payments:
        payment_date = get_payment_date(today, payment.payment_day)
        days_left = (payment_date - today).days

        reminder_days = [
            int(value)
            for value in payment.reminder_days.split(",")
            if value.strip().isdigit()
        ]

        if days_left in reminder_days:
            reminders.append({
                "id": payment.id,
                "title": payment.title,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_day": payment.payment_day,
                "days_left": days_left,
                "message": (
                    f"Сегодня необходимо оплатить «{payment.title}»"
                    if days_left == 0
                    else f"Через {days_left} дн. платеж «{payment.title}»"
                ),
            })

        if days_left == 0 and payment.last_charged_month != current_month:
            transaction = models.Transaction(
                user_id=current_user.id,
                category_id=payment.category_id,
                type="expense",
                amount=payment.amount,
                currency=payment.currency,
                comment=f"Автоматическое списание: {payment.title}",
            )

            db.add(transaction)
            payment.last_charged_month = current_month

    db.commit()

    return {
        "today": today,
        "reminders": reminders,
    }