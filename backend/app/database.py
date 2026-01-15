from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Создание engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    echo=settings.DEBUG  # Логирование SQL запросов в dev режиме
)

# Создание session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для получения сессии БД
def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания всех таблиц (для разработки)
def create_tables():
    """Создание всех таблиц в БД"""
    Base.metadata.create_all(bind=engine)