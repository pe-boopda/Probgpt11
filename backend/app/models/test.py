from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Test(Base):
    """Модель теста"""
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Настройки теста
    time_limit = Column(Integer, nullable=True)  # В минутах
    passing_score = Column(Integer, default=60)  # Процент для прохождения
    show_results = Column(Boolean, default=True)  # Показывать ли результаты после теста
    shuffle_questions = Column(Boolean, default=False)
    shuffle_options = Column(Boolean, default=False)
    
    # Доступность
    is_published = Column(Boolean, default=False)
    
    # Создатель теста
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_tests", foreign_keys=[creator_id])
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    test_sessions = relationship("TestSession", back_populates="test", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Test(id={self.id}, title={self.title})>"