from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.user import User, UserRole
from ..utils.security import get_current_user
from ..services.test_service import TestService
from ..schemas.test import (
    TestCreate,
    TestUpdate,
    TestResponse,
    TestDetailResponse,
    TestListItem,
    TestPublishRequest,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    TestStatistics,
    BulkDeleteRequest,
    BulkDeleteResponse
)

router = APIRouter()

# ============ Tests CRUD ============

@router.get("/", response_model=dict)
async def get_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    published_only: bool = False,
    my_tests: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список тестов с пагинацией и фильтрацией
    
    - **skip**: сколько записей пропустить
    - **limit**: максимальное количество записей
    - **search**: поиск по названию и описанию
    - **published_only**: только опубликованные тесты
    - **my_tests**: только мои тесты (для преподавателей)
    """
    creator_id = current_user.id if my_tests else None
    
    tests, total = TestService.get_tests(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        published_only=published_only,
        creator_id=creator_id
    )
    
    # Формирование ответа
    items = []
    for test in tests:
        info = TestService.calculate_test_info(test)
        items.append({
            "id": test.id,
            "title": test.title,
            "description": test.description,
            "is_published": test.is_published,
            "questions_count": info['questions_count'],
            "time_limit": test.time_limit,
            "passing_score": test.passing_score,
            "created_at": test.created_at,
            "creator_name": test.creator.full_name if test.creator else "Unknown"
        })
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }

@router.get("/{test_id}", response_model=TestDetailResponse)
async def get_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить детальную информацию о тесте с вопросами
    
    Студенты видят только опубликованные тесты.
    Преподаватели/админы видят все тесты.
    """
    test = TestService.get_test_by_id(db, test_id, include_questions=True)
    
    # Проверка доступа для студентов
    if current_user.role == UserRole.STUDENT:
        if not test.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
    
    # Вычисление информации
    info = TestService.calculate_test_info(test)
    
    return TestDetailResponse(
        id=test.id,
        title=test.title,
        description=test.description,
        time_limit=test.time_limit,
        passing_score=test.passing_score,
        show_results=test.show_results,
        shuffle_questions=test.shuffle_questions,
        shuffle_options=test.shuffle_options,
        is_published=test.is_published,
        creator_id=test.creator_id,
        created_at=test.created_at,
        updated_at=test.updated_at,
        questions_count=info['questions_count'],
        total_points=info['total_points'],
        questions=test.questions
    )

@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(
    test_data: TestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый тест
    
    Доступно только для преподавателей и администраторов.
    """
    # Проверка прав
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create tests"
        )
    
    test = TestService.create_test(db, test_data, current_user.id)
    info = TestService.calculate_test_info(test)
    
    return TestResponse(
        **test.__dict__,
        questions_count=info['questions_count'],
        total_points=info['total_points']
    )

@router.put("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    test_data: TestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить тест
    
    Только создатель теста может его редактировать.
    """
    test = TestService.update_test(db, test_id, test_data, current_user.id)
    info = TestService.calculate_test_info(test)
    
    return TestResponse(
        **test.__dict__,
        questions_count=info['questions_count'],
        total_points=info['total_points']
    )

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить тест
    
    Только создатель теста или администратор может его удалить.
    """
    test = TestService.get_test_by_id(db, test_id)
    
    # Админы могут удалять любые тесты
    if current_user.role == UserRole.ADMIN or test.creator_id == current_user.id:
        TestService.delete_test(db, test_id, current_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this test"
        )

# ============ Publish/Unpublish ============

@router.post("/{test_id}/publish", response_model=TestResponse)
async def publish_test(
    test_id: int,
    publish_data: TestPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Опубликовать или снять с публикации тест
    
    Только создатель теста может менять статус публикации.
    """
    test = TestService.publish_test(
        db, test_id, publish_data.is_published, current_user.id
    )
    info = TestService.calculate_test_info(test)
    
    return TestResponse(
        **test.__dict__,
        questions_count=info['questions_count'],
        total_points=info['total_points']
    )

# ============ Questions Management ============

@router.post("/{test_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_question(
    test_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Добавить вопрос к тесту
    
    Только создатель теста может добавлять вопросы.
    """
    question = TestService.add_question(db, test_id, question_data, current_user.id)
    return question

@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновить вопрос
    
    Только создатель теста может обновлять вопросы.
    """
    question = TestService.update_question(db, question_id, question_data, current_user.id)
    return question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удалить вопрос
    
    Только создатель теста может удалять вопросы.
    """
    TestService.delete_question(db, question_id, current_user.id)

# ============ Statistics ============

@router.get("/{test_id}/statistics", response_model=TestStatistics)
async def get_test_statistics(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по тесту
    
    Доступно только создателю теста или администратору.
    """
    test = TestService.get_test_by_id(db, test_id)
    
    # Проверка прав
    if current_user.role != UserRole.ADMIN and test.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view statistics for this test"
        )
    
    return TestService.get_test_statistics(db, test_id)

# ============ Bulk Operations ============

@router.post("/bulk/delete", response_model=BulkDeleteResponse)
async def bulk_delete_tests(
    delete_data: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Массовое удаление тестов
    
    Доступно только администраторам.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform bulk operations"
        )
    
    deleted_count = 0
    failed_ids = []
    
    for test_id in delete_data.test_ids:
        try:
            TestService.delete_test(db, test_id, current_user.id)
            deleted_count += 1
        except Exception:
            failed_ids.append(test_id)
    
    return BulkDeleteResponse(
        deleted_count=deleted_count,
        failed_ids=failed_ids
    )