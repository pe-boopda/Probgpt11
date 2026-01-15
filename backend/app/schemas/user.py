from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from ..models.user import UserRole

# Базовые схемы
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.STUDENT

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str = Field(min_length=6, max_length=72)

class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    group_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    is_active: bool
    group_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для аутентификации
class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Payload JWT токена"""
    sub: int  # user_id
    exp: datetime
    type: str

class LoginRequest(BaseModel):
    """Схема запроса на вход"""
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=6, max_length=72)
