from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from datetime import datetime, date


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6)
    password_repeat: str = Field(min_length=6)
    main_currency: str = "RUB"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str
    color: Optional[str] = None
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    category_id: int
    type: str
    amount: float
    currency: str
    comment: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    category_id: int
    type: str
    amount: float
    currency: str
    date: datetime
    comment: Optional[str]

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    comment: Optional[str] = None

class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    target_amount: float
    current_amount: float = 0
    currency: str = "RUB"
    deadline: Optional[date] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    currency: Optional[str] = None
    deadline: Optional[date] = None


class GoalResponse(BaseModel):
    id: int
    title: str
    target_amount: float
    current_amount: float
    currency: str
    deadline: Optional[date]
    progress_percent: float

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    main_currency: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    main_currency: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class RecurringPaymentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    amount: float
    currency: str = "RUB"
    category_id: int
    payment_day: int = Field(ge=1, le=31)


class RecurringPaymentUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    category_id: Optional[int] = None
    payment_day: Optional[int] = Field(default=None, ge=1, le=31)
    is_active: Optional[int] = None


class RecurringPaymentResponse(BaseModel):
    id: int
    title: str
    amount: float
    currency: str
    category_id: int
    payment_day: int
    reminder_days: str
    is_active: int
    last_charged_month: Optional[str] = None

    class Config:
        from_attributes = True


class GoalContributionCreate(BaseModel):
    amount: float
    currency: str = "RUB"
    comment: Optional[str] = None


class GoalContributionResponse(BaseModel):
    id: int
    goal_id: int
    amount: float
    currency: str
    date: datetime
    comment: Optional[str] = None

    class Config:
        from_attributes = True