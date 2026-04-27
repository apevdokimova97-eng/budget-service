from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routers import auth, categories, transactions, statistics, goals, assistant, users, recurring_payments


app = FastAPI(
    title="Budget Service API",
    description="API для сервиса учета и планирования личного бюджета",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8100",
        "http://127.0.0.1:8100",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(statistics.router)
app.include_router(goals.router)
app.include_router(assistant.router)
app.include_router(users.router)
app.include_router(recurring_payments.router)

@app.get("/")
def root():
    return {"message": "Budget Service API is working"}