from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

from typing import Optional
from datetime import date, datetime, time

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=schemas.TransactionResponse)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if transaction.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Invalid type")

    category = db.query(models.Category).filter(
        models.Category.id == transaction.category_id,
        models.Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_transaction = models.Transaction(
        user_id=current_user.id,
        category_id=transaction.category_id,
        type=transaction.type,
        amount=transaction.amount,
        currency=transaction.currency,
        comment=transaction.comment
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/", response_model=list[schemas.TransactionResponse])
def get_transactions(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    )

    if date_from:
        query = query.filter(
            models.Transaction.date >= datetime.combine(date_from, time.min)
        )

    if date_to:
        query = query.filter(
            models.Transaction.date <= datetime.combine(date_to, time.max)
        )

    return query.order_by(models.Transaction.date.desc()).all()


@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id,
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = transaction_data.model_dump(exclude_unset=True)

    if "type" in update_data:
        if update_data["type"] not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="Invalid type")

    if "category_id" in update_data:
        category = db.query(models.Category).filter(
            models.Category.id == update_data["category_id"],
            models.Category.user_id == current_user.id,
        ).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted"}