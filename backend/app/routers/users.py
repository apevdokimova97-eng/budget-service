from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user),
):
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_me(
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user