# backend/app/api/sessions.py
"""
API endpoints for test sessions - Updated to restrict student access to results
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.test import Test
from app.models.session import TestSession
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionDetailResponse,
    AnswerSubmit,
    SessionResultResponse,
)
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/tests/{test_id}/start", response_model=SessionResponse)
async def start_test_session(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start a new test session or return existing active session.
    Available to: Students
    """
    service = SessionService(db)
    
    # Check if test exists and is published
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if not test.is_published:
        raise HTTPException(status_code=403, detail="Test is not published")
    
    # Check for existing active session
    existing_session = service.get_active_session(test_id, current_user.id)
    if existing_session:
        return existing_session
    
    # Create new session
    session = service.create_session(test_id, current_user.id)
    return session


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get session details.
    Students can only access their own sessions.
    Teachers/Admins can access any session.
    """
    service = SessionService(db)
    session = service.get_session(session_id)
    
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        if session.student_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own sessions"
            )
    
    return session


@router.post("/sessions/{session_id}/answer")
async def submit_answer(
    session_id: int,
    answer: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit an answer for a question.
    Available to: Students (only their own sessions)
    """
    service = SessionService(db)
    session = service.get_session(session_id)
    
    # Check if student owns this session
    if session.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only submit answers to your own sessions"
        )
    
    # Check if session is still active
    if session.status != "in_progress":
        raise HTTPException(
            status_code=400,
            detail="Cannot submit answers to a completed session"
        )
    
    result = service.submit_answer(session_id, answer)
    return result


@router.post("/sessions/{session_id}/submit")
async def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Complete the test session and calculate results.
    Available to: Students (only their own sessions)
    """
    service = SessionService(db)
    session = service.get_session(session_id)
    
    # Check if student owns this session
    if session.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only complete your own sessions"
        )
    
    # Check if session is still active
    if session.status != "in_progress":
        raise HTTPException(
            status_code=400,
            detail="Session is already completed"
        )
    
    result = service.complete_session(session_id)
    return result


@router.get("/sessions/{session_id}/result", response_model=SessionResultResponse)
async def get_session_result(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get session results.
    
    IMPORTANT: Students CANNOT access their results.
    Only Teachers and Admins can view results.
    """
    service = SessionService(db)
    session = service.get_session(session_id)
    
    # STUDENTS ARE NOT ALLOWED TO VIEW RESULTS
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view test results. Please contact your teacher."
        )
    
    # Teachers can only view results for their tests
    if current_user.role == UserRole.TEACHER:
        test = db.query(Test).filter(Test.id == session.test_id).first()
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view results for your own tests"
            )
    
    # Admins can view any results
    result = service.get_session_result(session_id)
    return result


@router.get("/sessions/{session_id}/progress")
async def get_session_progress(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get session progress (without showing answers).
    Available to: Students (their own), Teachers, Admins
    """
    service = SessionService(db)
    session = service.get_session(session_id)
    
    # Students can only see their own progress
    if current_user.role == UserRole.STUDENT:
        if session.student_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own progress"
            )
    
    progress = service.get_session_progress(session_id)
    return progress


# NEW: Teacher/Admin endpoint to view all session results for a test
@router.get("/tests/{test_id}/results", response_model=List[SessionResultResponse])
async def get_test_results(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all session results for a test.
    Available to: Teachers (their tests), Admins (all tests)
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view test results"
        )
    
    if current_user.role == UserRole.TEACHER:
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view results for your own tests"
            )
    
    # Get all completed sessions for this test
    sessions = (
        db.query(TestSession)
        .filter(
            TestSession.test_id == test_id,
            TestSession.status == "completed"
        )
        .all()
    )
    
    service = SessionService(db)
    results = [service.get_session_result(session.id) for session in sessions]
    return results


# NEW: Teacher/Admin endpoint to view specific student's result
@router.get(
    "/tests/{test_id}/students/{student_id}/result",
    response_model=SessionResultResponse
)
async def get_student_test_result(
    test_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific student's result for a test.
    Available to: Teachers (their tests), Admins (all tests)
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view test results"
        )
    
    if current_user.role == UserRole.TEACHER:
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view results for your own tests"
            )
    
    # Find the session
    session = (
        db.query(TestSession)
        .filter(
            TestSession.test_id == test_id,
            TestSession.student_id == student_id,
            TestSession.status == "completed"
        )
        .order_by(TestSession.completed_at.desc())
        .first()
    )
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="No completed session found for this student"
        )
    
    service = SessionService(db)
    result = service.get_session_result(session.id)
    return result