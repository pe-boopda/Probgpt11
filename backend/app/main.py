from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from .config import settings
from .database import engine, Base

# ВАЖНО: импортируем модели ДО create_all, чтобы таблицы реально создались
from .models import user, group, test, question, session, image  # noqa: F401

from .api import auth, tests, sessions, statistics, images


# Создание директории для загрузок
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="Testing System"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы (загруженные изображения)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# --- ROUTERS ---
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tests.router, prefix="/api/tests", tags=["Tests"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["Statistics"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])


@app.on_event("startup")
def on_startup():
    # Создание таблиц при старте (для разработки)
    # В production лучше использовать Alembic
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
