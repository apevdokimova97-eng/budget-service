from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models, schemas
from app.auth_utils import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])


DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Дом", "color": "#ff8c32", "icon": "home"},
    {"name": "Досуг", "color": "#35b8a6", "icon": "wallet"},
    {"name": "Здоровье", "color": "#ff3b3b", "icon": "heart"},
    {"name": "Кафе", "color": "#9b7be9", "icon": "cafe"},
    {"name": "Образование", "color": "#3a9edb", "icon": "education"},
    {"name": "Подарки", "color": "#e24d8e", "icon": "gift"},
    {"name": "Продукты", "color": "#61b947", "icon": "basket"},
    {"name": "Семья", "color": "#f5b400", "icon": "family"},
    {"name": "Спорт", "color": "#f27611", "icon": "sport"},
    {"name": "Транспорт", "color": "#2f80d1", "icon": "transport"},
]

DEFAULT_INCOME_CATEGORIES = [
    {"name": "Зарплата", "color": "#2f80d1", "icon": "salary"},
    {"name": "Подарок", "color": "#e24d8e", "icon": "gift"},
    {"name": "Проценты по вкладу", "color": "#61b947", "icon": "bank"},
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_default_categories(db: Session, user_id: int):
    for category in DEFAULT_EXPENSE_CATEGORIES:
        db.add(
            models.Category(
                user_id=user_id,
                name=category["name"],
                type="expense",
                color=category["color"],
                icon=category["icon"],
            )
        )

    for category in DEFAULT_INCOME_CATEGORIES:
        db.add(
            models.Category(
                user_id=user_id,
                name=category["name"],
                type="income",
                color=category["color"],
                icon=category["icon"],
            )
        )


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email уже существует")

    if user.password != user.password_repeat:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    new_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
        main_currency=user.main_currency,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_default_categories(db, new_user.id)
    db.commit()

    return {"message": "User created"}


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный пароль")

    token = create_token({"user_id": db_user.id})

    return {"access_token": token}