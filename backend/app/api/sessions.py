from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..utils.security import get_current_user
from ..services.session_service import SessionService
from ..schemas.session import (
    SessionStart,
    SessionResponse,
    AnswerSubmit,
    AnswerResponse,
    SessionSubmit,
    SessionResult,
    TestForStudent,
    SessionProgress
)

router = APIRouter()

# ============ Start Test ============

@router.post("/tests/{test_id}/start", response_model=SessionResponse)
async def start_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Начать прохождение теста
    
    Создает новую сессию или возвращает существующую активную сессию.
    """
    session = SessionService.start_test(db, test_id, current_user.id)
    
    time_remaining = SessionService.get_time_remaining(session)
    
    return SessionResponse(
        id=session.id,
        test_id=session.test_id,
        user_id=session.user_id,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        total_questions=session.total_questions,
        answered_questions=session.answered_questions,
        time_remaining=time_remaining
    )

# ============ Get Session ============

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить информацию о сессии
    """
    session = SessionService.get_session(db, session_id, current_user.id)
    time_remaining = SessionService.get_time_remaining(session)
    
    return SessionResponse(
        id=session.id,
        test_id=session.test_id,
        user_id=session.user_id,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        total_questions=session.total_questions,
        answered_questions=session.answered_questions,
        time_remaining=time_remaining
    )

# ============ Get Test Questions ============

@router.get("/sessions/{session_id}/test", response_model=TestForStudent)
async def get_test_questions(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить вопросы теста для прохождения
    
    Возвращает вопросы БЕЗ информации о правильных ответах.
    """
    session = SessionService.get_session(db, session_id, current_user.id)
    
    if session.status != 'in_progress':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not active"
        )
    
    test_data = SessionService.get_test_for_session(
        db,
        session,
        shuffle_options=session.test.shuffle_options
    )
    
    return TestForStudent(**test_data)

# ============ Submit Answer ============

@router.post("/sessions/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: int,
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отправить ответ на вопрос
    
    **answer_data** зависит от типа вопроса:
    
    - **multiple_choice**: `{"selected_option_id": 123}`
    - **multiple_select**: `{"selected_option_ids": [123, 456]}`
    - **true_false**: `{"selected_option_id": 123}`
    - **text_input**: `{"text": "My answer"}`
    - **image_annotation**: `{"annotations": [...]}`
    """
    answer = SessionService.submit_answer(
        db,
        session_id,
        answer_data.question_id,
        answer_data.answer_data,
        current_user.id
    )
    
    return AnswerResponse(
        id=answer.id,
        question_id=answer.question_id,
        answer_data=answer.answer_data,
        answered_at=answer.answered_at
    )

# ============ Submit Test ============

@router.post("/sessions/{session_id}/submit", response_model=SessionResult)
async def submit_test(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Завершить тест и получить результаты
    
    Вычисляет правильность ответов и итоговый балл.
    """
    result = SessionService.submit_test(db, session_id, current_user.id)
    return SessionResult(**result)

# ============ Get Results ============

@router.get("/sessions/{session_id}/result", response_model=SessionResult)
async def get_result(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить результаты завершенного теста
    """
    result = SessionService.get_result(db, session_id, current_user.id)
    return SessionResult(**result)

# ============ Get Progress ============

@router.get("/sessions/{session_id}/progress", response_model=SessionProgress)
async def get_progress(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить прогресс прохождения теста
    """
    session = SessionService.get_session(db, session_id, current_user.id)
    time_remaining = SessionService.get_time_remaining(session)
    
    # Определить текущий вопрос
    answered = db.query(Answer).filter(
        Answer.session_id == session_id
    ).count()
    
    return SessionProgress(
        session_id=session.id,
        total_questions=session.total_questions,
        answered_questions=answered,
        current_question=answered,
        time_remaining=time_remaining
    )