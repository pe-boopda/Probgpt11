# Основные настройки
APP_NAME="Testing System"
VERSION="1.0.0"
DEBUG=True

# База данных PostgreSQL
DATABASE_URL=postgresql://testuser:testpass@localhost:5432/testingdb

# JWT Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (разрешенные origins)
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Файлы
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_IMAGE_TYPES=["image/jpeg","image/png","image/gif"]

# Пагинация
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100