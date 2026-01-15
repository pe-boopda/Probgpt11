from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class SessionStatus(str, enum.Enum):
    """Статусы сессии тестирования"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    ABANDONED = "abandoned"

class TestSession(Base):
    """Модель сессии прохождения теста"""
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Статус и время
    status = Column(Enum(SessionStatus), default=SessionStatus.IN_PROGRESS)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Результаты
    total_questions = Column(Integer, default=0)
    answered_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score = Column(Float, default=0.0)  # Процент правильных ответов
    points_earned = Column(Float, default=0.0)  # Набранные баллы
    max_points = Column(Float, default=0.0)  # Максимально возможные баллы
    
    # Дополнительные данные (порядок вопросов, время на каждый вопрос и т.д.)
    meta = Column("metadata", JSON, nullable=True)
    
    # Relationships
    test = relationship("Test", back_populates="test_sessions")
    user = relationship("User", back_populates="test_sessions")
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TestSession(id={self.id}, user_id={self.user_id}, status={self.status})>"

class Answer(Base):
    """Модель ответа на вопрос"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Ответ зависит от типа вопроса:
    # - для multiple_choice: ID выбранного варианта
    # - для text_input: текст ответа
    # - для image_annotation: JSON с координатами и аннотациями
    # - для matching: JSON с парами
    answer_data = Column(JSON, nullable=False)
    
    # Проверка
    is_correct = Column(Integer, nullable=True)  # null если не проверен
    points_awarded = Column(Float, default=0.0)
    
    # Timestamps
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("TestSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"