from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.user import User, UserRole
from ..utils.security import get_current_user, require_role
from ..services.statistics_service import StatisticsService
from ..schemas.statistics import (
    DashboardStats,
    TestDetailedStats,
    TestQuestionBreakdown,
    StudentStats,
    GroupStats,
    Leaderboard
)

router = APIRouter()

# ============ Dashboard Statistics ============

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics(
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """
    Получить общую статистику для дашборда
    
    Доступно только преподавателям и администраторам.
    """
    stats = StatisticsService.get_dashboard_stats(db, current_user.id)
    return DashboardStats(**stats)

# ============ Test Statistics ============

@router.get("/tests/{test_id}", response_model=TestDetailedStats)
async def get_test_statistics(
    test_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """
    Получить детальную статистику по тесту
    
    Включает:
    - Количество попыток
    - Средний балл, медиану, мин/макс
    - Процент прохождения
    - Среднее время
    - Статистику по вопросам
    """
    stats = StatisticsService.get_test_detailed_stats(db, test_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    return TestDetailedStats(**stats)

@router.get("/tests/{test_id}/questions", response_model=TestQuestionBreakdown)
async def get_test_question_breakdown(
    test_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по каждому вопросу теста
    
    Показывает:
    - Процент правильных ответов
    - Сложность вопроса
    - Количество ответов
    """
    breakdown = StatisticsService.get_question_breakdown(db, test_id)
    
    if not breakdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    return TestQuestionBreakdown(**breakdown)

# ============ Student Statistics ============

@router.get("/students/{student_id}", response_model=StudentStats)
async def get_student_statistics(
    student_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по студенту
    
    Включает:
    - Количество пройденных тестов
    - Средний балл
    - Процент прохождения
    - Общее время
    """
    stats = StatisticsService.get_student_stats(db, student_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return StudentStats(**stats)

# ============ Group Statistics ============

@router.get("/groups/{group_id}", response_model=GroupStats)
async def get_group_statistics(
    group_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по группе
    
    Включает:
    - Количество студентов
    - Средний балл группы
    - Лучший/худший студент
    - Общую активность
    """
    stats = StatisticsService.get_group_stats(db, group_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return GroupStats(**stats)

# ============ Leaderboard ============

@router.get("/leaderboard", response_model=Leaderboard)
async def get_leaderboard(
    test_id: Optional[int] = None,
    group_id: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить таблицу лидеров
    
    Параметры:
    - test_id: фильтр по конкретному тесту
    - group_id: фильтр по группе
    - limit: количество записей (по умолчанию 10)
    """
    entries = StatisticsService.get_leaderboard(
        db,
        test_id=test_id,
        group_id=group_id,
        limit=limit
    )
    
    return Leaderboard(
        test_id=test_id,
        group_id=group_id,
        period="all_time",
        entries=entries
    )

# ============ Performance Trend ============

@router.get("/trend")
async def get_performance_trend(
    test_id: Optional[int] = None,
    group_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """
    Получить тренд успеваемости по дням
    
    Возвращает данные для построения графика изменения
    среднего балла во времени.
    """
    trend_data = StatisticsService.get_performance_trend(
        db,
        test_id=test_id,
        group_id=group_id,
        period="daily",
        days=days
    )
    
    return {
        "label": "Average Score",
        "data": trend_data
    }