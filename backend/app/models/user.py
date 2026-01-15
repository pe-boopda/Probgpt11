from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class UserRole(str, enum.Enum):
    """Роли пользователей"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Связь с группой (для студентов)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    group = relationship("Group", back_populates="students")
    test_sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")
    created_tests = relationship("Test", back_populates="creator", foreign_keys="Test.creator_id")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"