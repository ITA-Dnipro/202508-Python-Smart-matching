# app/main.py
from fastapi import FastAPI
from app.api.routes import router
from app.services.db import init_db

app = FastAPI(title="Smart Matcher Service")

@app.on_event("startup")
def on_startup():
    # ініціалізація БД/схеми, якщо потрібно
    init_db()

# підключаємо роутери
app.include_router(router)
