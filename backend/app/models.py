from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

from sqlalchemy import Float, DateTime, Date
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    main_currency = Column(String(10), nullable=False, default="RUB")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # income / expense
    color = Column(String(20), nullable=True)
    icon = Column(String(100), nullable=True)

    user = relationship("User")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    type = Column(String(20), nullable=False)  # income / expense
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)

    date = Column(DateTime, default=datetime.utcnow)
    comment = Column(String(255), nullable=True)

    user = relationship("User")
    category = relationship("Category")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(150), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False, default=0)
    currency = Column(String(10), nullable=False)
    deadline = Column(Date, nullable=True)

    user = relationship("User")


class RecurringPayment(Base):
    __tablename__ = "recurring_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    title = Column(String(150), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    payment_day = Column(Integer, nullable=False)  # день месяца: 1-31
    reminder_days = Column(String(50), nullable=False, default="3,1,0")
    is_active = Column(Integer, nullable=False, default=1)

    last_charged_month = Column(String(7), nullable=True)  # например 2026-04

    user = relationship("User")
    category = relationship("Category")


class GoalContribution(Base):
    __tablename__ = "goal_contributions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    comment = Column(String(255), nullable=True)

    user = relationship("User")
    goal = relationship("Goal")