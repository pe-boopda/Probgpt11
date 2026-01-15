from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from ..models.session import SessionStatus

# ============ Session Schemas ============

class SessionStart(BaseModel):
    """Запрос на начало теста"""
    pass

class SessionResponse(BaseModel):
    """Ответ с информацией о сессии"""
    id: int
    test_id: int
    user_id: int
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    total_questions: int
    answered_questions: int
    time_remaining: Optional[int] = None  # В секундах
    
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    """Отправка ответа на вопрос"""
    question_id: int
    answer_data: Any  # JSON - зависит от типа вопроса
    
class AnswerResponse(BaseModel):
    """Ответ после сохранения"""
    id: int
    question_id: int
    answer_data: Any
    answered_at: datetime
    
    class Config:
        from_attributes = True

class SessionSubmit(BaseModel):
    """Завершение теста"""
    pass

class SessionResult(BaseModel):
    """Результаты прохождения теста"""
    session_id: int
    test_title: str
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    time_taken_minutes: Optional[float]
    
    # Результаты
    total_questions: int
    answered_questions: int
    correct_answers: int
    score: float  # Процент правильных
    points_earned: float
    max_points: float
    passed: bool
    
    # Детали по вопросам (если show_results=True)
    questions_details: Optional[List[dict]] = None

class SessionProgress(BaseModel):
    """Прогресс прохождения теста"""
    session_id: int
    total_questions: int
    answered_questions: int
    current_question: int
    time_remaining: Optional[int] = None
    
# ============ Question for Student ============

class QuestionForStudent(BaseModel):
    """Вопрос для студента (без правильных ответов)"""
    id: int
    question_type: str
    question_text: str
    points: float
    image_id: Optional[int]
    order: int
    options: List[dict] = []  # Без is_correct
    metadata: Optional[dict] = None

class TestForStudent(BaseModel):
    """Тест для прохождения студентом"""
    id: int
    title: str
    description: Optional[str]
    time_limit: Optional[int]
    passing_score: int
    total_questions: int
    total_points: float
    shuffle_questions: bool
    shuffle_options: bool
    questions: List[QuestionForStudent]

# ============ Statistics ============

class UserTestHistory(BaseModel):
    """История прохождения тестов пользователем"""
    test_id: int
    test_title: str
    attempts: int
    best_score: float
    last_attempt: datetime
    passed: bool