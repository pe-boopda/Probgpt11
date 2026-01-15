from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.question import QuestionType

# ============ Question Schemas ============

class QuestionOptionBase(BaseModel):
    """Базовая схема для варианта ответа"""
    option_text: str
    is_correct: bool = False
    order: int = 0
    match_id: Optional[str] = None

class QuestionOptionCreate(QuestionOptionBase):
    """Создание варианта ответа"""
    pass

class QuestionOptionResponse(QuestionOptionBase):
    """Ответ с вариантом ответа"""
    id: int
    question_id: int
    
    class Config:
        from_attributes = True

# ============ Question Base Schemas ============

class QuestionBase(BaseModel):
    """Базовая схема вопроса"""
    question_type: QuestionType
    question_text: str
    order: int = 0
    points: float = Field(default=1.0, ge=0)
    image_id: Optional[int] = None
    metadata: Optional[dict] = None

class QuestionCreate(QuestionBase):
    """Создание вопроса"""
    options: List[QuestionOptionCreate] = []

class QuestionUpdate(BaseModel):
    """Обновление вопроса"""
    question_text: Optional[str] = None
    order: Optional[int] = None
    points: Optional[float] = Field(None, ge=0)
    image_id: Optional[int] = None
    metadata: Optional[dict] = None
    options: Optional[List[QuestionOptionCreate]] = None

class QuestionResponse(QuestionBase):
    """Ответ с вопросом"""
    id: int
    test_id: int
    options: List[QuestionOptionResponse] = []
    
    class Config:
        from_attributes = True

class QuestionPreview(BaseModel):
    """Краткая информация о вопросе (без правильных ответов)"""
    id: int
    question_type: QuestionType
    question_text: str
    order: int
    points: float
    image_id: Optional[int]
    # Опции без информации о правильности
    options: List[dict] = []  # Без is_correct
    
    class Config:
        from_attributes = True

# ============ Test Schemas ============

class TestBase(BaseModel):
    """Базовая схема теста"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    time_limit: Optional[int] = Field(None, ge=1, description="Время в минутах")
    passing_score: int = Field(default=60, ge=0, le=100, description="Проходной балл в %")
    show_results: bool = True
    shuffle_questions: bool = False
    shuffle_options: bool = False

class TestCreate(TestBase):
    """Создание теста"""
    pass

class TestUpdate(BaseModel):
    """Обновление теста"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    time_limit: Optional[int] = Field(None, ge=1)
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    show_results: Optional[bool] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None

class TestResponse(TestBase):
    """Полный ответ с тестом"""
    id: int
    is_published: bool
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    questions_count: int = 0
    total_points: float = 0.0
    
    class Config:
        from_attributes = True

class TestDetailResponse(TestResponse):
    """Детальная информация о тесте с вопросами"""
    questions: List[QuestionResponse] = []

class TestPreview(TestBase):
    """Превью теста для студентов (без правильных ответов)"""
    id: int
    is_published: bool
    created_at: datetime
    questions_count: int
    total_points: float
    
    class Config:
        from_attributes = True

class TestListItem(BaseModel):
    """Элемент списка тестов"""
    id: int
    title: str
    description: Optional[str]
    is_published: bool
    questions_count: int
    time_limit: Optional[int]
    passing_score: int
    created_at: datetime
    creator_name: str
    
    class Config:
        from_attributes = True

# ============ Test Statistics ============

class TestStatistics(BaseModel):
    """Статистика по тесту"""
    test_id: int
    total_attempts: int
    completed_attempts: int
    average_score: float
    pass_rate: float
    average_time_minutes: float
    
# ============ Publish/Unpublish ============

class TestPublishRequest(BaseModel):
    """Запрос на публикацию/снятие с публикации"""
    is_published: bool

# ============ Bulk Operations ============

class BulkDeleteRequest(BaseModel):
    """Массовое удаление"""
    test_ids: List[int] = Field(..., min_items=1)

class BulkDeleteResponse(BaseModel):
    """Ответ на массовое удаление"""
    deleted_count: int
    failed_ids: List[int] = []