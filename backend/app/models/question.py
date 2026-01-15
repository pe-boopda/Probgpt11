from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class QuestionType(str, enum.Enum):
    """Типы вопросов"""
    MULTIPLE_CHOICE = "multiple_choice"  # Один правильный ответ
    MULTIPLE_SELECT = "multiple_select"  # Несколько правильных ответов
    TRUE_FALSE = "true_false"  # Правда/Ложь
    TEXT_INPUT = "text_input"  # Текстовое поле
    IMAGE_ANNOTATION = "image_annotation"  # Рисование на изображении
    MATCHING = "matching"  # Таблица соответствий
    ORDERING = "ordering"  # Упорядочивание
    HOTSPOT = "hotspot"  # Выбор области на изображении
    FILL_BLANKS = "fill_blanks"  # Заполнение пропусков

class Question(Base):
    """Модель вопроса"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    
    # Содержание вопроса
    question_type = Column(Enum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    order = Column(Integer, default=0)  # Порядок вопроса в тесте
    points = Column(Float, default=1.0)  # Баллы за вопрос
    
    # Изображение (если есть)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    
    # Дополнительные данные (зависит от типа вопроса)
    # Для image_annotation: разметка областей
    # Для matching: пары соответствий
    # Для ordering: правильный порядок
    meta = Column("metadata", JSON, nullable=True)

    
    # Relationships
    test = relationship("Test", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    image = relationship("Image", foreign_keys=[image_id])
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type={self.question_type})>"

class QuestionOption(Base):
    """Модель варианта ответа"""
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    option_text = Column(Text, nullable=False)
    is_correct = Column(Integer, default=0)  # 0 или 1 (для multiple_select может быть несколько)
    order = Column(Integer, default=0)
    
    # Для matching вопросов - ID пары
    match_id = Column(String(50), nullable=True)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    
    def __repr__(self):
        return f"<QuestionOption(id={self.id}, is_correct={self.is_correct})>"