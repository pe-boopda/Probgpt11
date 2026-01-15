from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Конфигурация приложения"""
    
    # Основные настройки
    APP_NAME: str = "Testing System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # База данных
    DATABASE_URL: str = "postgresql://testuser:testpass@localhost:5432/testingdb"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Файлы
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif"]
    
    # Пагинация
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()