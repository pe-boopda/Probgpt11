from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

# ============ Dashboard Statistics ============

class DashboardStats(BaseModel):
    """Общая статистика для дашборда"""
    total_tests: int
    total_students: int
    total_sessions: int
    total_groups: int
    published_tests: int
    active_sessions: int
    average_score: float
    tests_this_month: int

# ============ Test Statistics ============

class TestDetailedStats(BaseModel):
    """Детальная статистика по тесту"""
    test_id: int
    test_title: str
    
    # Общее
    total_attempts: int
    completed_attempts: int
    in_progress: int
    abandoned: int
    
    # Результаты
    average_score: float
    median_score: float
    min_score: float
    max_score: float
    pass_rate: float  # Процент прошедших
    
    # Время
    average_time_minutes: float
    min_time_minutes: float
    max_time_minutes: float
    
    # Вопросы
    total_questions: int
    average_correct_per_student: float
    
    # По датам
    last_attempt: Optional[datetime]
    first_attempt: Optional[datetime]

class QuestionStats(BaseModel):
    """Статистика по вопросу"""
    question_id: int
    question_text: str
    question_type: str
    points: float
    
    # Статистика
    total_answers: int
    correct_answers: int
    incorrect_answers: int
    unanswered: int
    
    # Проценты
    correct_rate: float  # Процент правильных
    difficulty: str  # easy, medium, hard
    
    # Время
    average_time_seconds: Optional[float]

class TestQuestionBreakdown(BaseModel):
    """Разбивка по вопросам"""
    test_id: int
    questions: List[QuestionStats]

# ============ Student Statistics ============

class StudentStats(BaseModel):
    """Статистика по студенту"""
    student_id: int
    student_name: str
    email: str
    group_name: Optional[str]
    
    # Общее
    total_tests_taken: int
    completed_tests: int
    average_score: float
    total_points_earned: float
    
    # Прогресс
    tests_passed: int
    tests_failed: int
    pass_rate: float
    
    # Активность
    last_test_date: Optional[datetime]
    total_time_spent_minutes: float

class StudentTestHistory(BaseModel):
    """История тестов студента"""
    student_id: int
    student_name: str
    tests: List[dict]  # Список тестов с результатами

# ============ Group Statistics ============

class GroupStats(BaseModel):
    """Статистика по группе"""
    group_id: int
    group_name: str
    
    # Студенты
    total_students: int
    active_students: int
    
    # Тесты
    total_tests_assigned: int
    total_attempts: int
    average_score: float
    
    # Сравнение
    best_student: Optional[str]
    worst_student: Optional[str]
    median_score: float

class GroupComparison(BaseModel):
    """Сравнение групп"""
    groups: List[Dict]  # Список групп с метриками

# ============ Time Series ============

class TimeSeriesPoint(BaseModel):
    """Точка временного ряда"""
    date: str  # YYYY-MM-DD
    value: float
    count: int

class TimeSeriesData(BaseModel):
    """Данные временного ряда"""
    label: str
    data: List[TimeSeriesPoint]

class PerformanceTrend(BaseModel):
    """Тренд успеваемости"""
    period: str  # daily, weekly, monthly
    metrics: List[TimeSeriesData]

# ============ Leaderboard ============

class LeaderboardEntry(BaseModel):
    """Запись в таблице лидеров"""
    rank: int
    student_id: int
    student_name: str
    score: float
    tests_completed: int
    group_name: Optional[str]

class Leaderboard(BaseModel):
    """Таблица лидеров"""
    test_id: Optional[int]
    group_id: Optional[int]
    period: str  # all_time, month, week
    entries: List[LeaderboardEntry]

# ============ Export ============

class ExportRequest(BaseModel):
    """Запрос на экспорт"""
    format: str  # csv, excel, pdf
    test_ids: Optional[List[int]]
    group_ids: Optional[List[int]]
    student_ids: Optional[List[int]]
    date_from: Optional[datetime]
    date_to: Optional[datetime]

class ExportResponse(BaseModel):
    """Ответ с файлом для скачивания"""
    file_url: str
    filename: str
    expires_at: datetime