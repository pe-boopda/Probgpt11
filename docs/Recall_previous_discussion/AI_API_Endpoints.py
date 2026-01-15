# backend/app/api/ai_grading.py
"""
API endpoints for AI-powered grading functionality
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.test import Test
from app.models.session import TestSession, Answer
from app.services.session_service import SessionService


router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class RegradeRequest(BaseModel):
    use_stricter_threshold: bool = False


class BatchRegradeRequest(BaseModel):
    session_ids: Optional[List[int]] = None  # If None, regrade all


class AIFeedbackResponse(BaseModel):
    answer_id: int
    ai_feedback: dict
    quality_metrics: Optional[dict]


class SuggestionsResponse(BaseModel):
    answer_id: int
    suggestions: List[str]


class PlagiarismCheckResponse(BaseModel):
    total_checked: int
    suspicious_count: int
    suspicious_answers: List[dict]


# ==================== ENDPOINTS ====================

@router.get("/answers/{answer_id}/ai-feedback")
async def get_ai_feedback(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI feedback for a specific answer
    
    Available to: Teachers, Admins
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view AI feedback"
        )
    
    try:
        service = SessionService(db, use_ai_grading=True)
        result = service.get_answer_with_ai_feedback(answer_id)
        
        return AIFeedbackResponse(
            answer_id=answer_id,
            ai_feedback=result.get('ai_feedback'),
            quality_metrics=result.get('quality_metrics')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answers/{answer_id}/regrade")
async def regrade_answer(
    answer_id: int,
    request: RegradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Re-grade a text answer using AI
    
    Available to: Teachers, Admins
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot regrade answers"
        )
    
    # Get answer and check ownership
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    session = answer.session
    test = db.query(Test).filter(Test.id == session.test_id).first()
    
    if current_user.role == UserRole.TEACHER:
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only regrade answers for your own tests"
            )
    
    try:
        service = SessionService(db, use_ai_grading=True)
        result = service.regrade_text_answer_with_ai(
            answer_id=answer_id,
            use_stricter_threshold=request.use_stricter_threshold
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/regrade-all")
async def regrade_session(
    session_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Re-grade all text answers in a session using AI
    Runs in background for large sessions
    
    Available to: Teachers, Admins
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot regrade sessions"
        )
    
    # Get session and check ownership
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    test = db.query(Test).filter(Test.id == session.test_id).first()
    
    if current_user.role == UserRole.TEACHER:
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only regrade your own tests"
            )
    
    try:
        service = SessionService(db, use_ai_grading=True)
        
        # Execute regrading in background
        def regrade_task():
            result = service.batch_regrade_text_answers(session_id)
            # TODO: Send notification to teacher when done
            return result
        
        background_tasks.add_task(regrade_task)
        
        return {
            "success": True,
            "message": "Regrading started in background",
            "session_id": session_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tests/{test_id}/regrade-all")
async def regrade_test_sessions(
    test_id: int,
    request: BatchRegradeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Re-grade all text answers in a test (all sessions)
    Useful after adjusting question criteria
    
    Available to: Teachers (their tests), Admins (all tests)
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot regrade tests"
        )
    
    # Get test and check ownership
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if current_user.role == UserRole.TEACHER:
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only regrade your own tests"
            )
    
    # Get sessions to regrade
    if request.session_ids:
        sessions = (
            db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.id.in_(request.session_ids),
                TestSession.status == "completed"
            )
            .all()
        )
    else:
        sessions = (
            db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.status == "completed"
            )
            .all()
        )
    
    try:
        service = SessionService(db, use_ai_grading=True)
        
        def regrade_all_task():
            results = []
            for session in sessions:
                try:
                    result = service.batch_regrade_text_answers(session.id)
                    results.append({
                        'session_id': session.id,
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'session_id': session.id,
                        'error': str(e)
                    })
            return results
        
        background_tasks.add_task(regrade_all_task)
        
        return {
            "success": True,
            "message": f"Regrading {len(sessions)} sessions in background",
            "test_id": test_id,
            "session_count": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/answers/{answer_id}/suggestions")
async def get_improvement_suggestions(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI-powered improvement suggestions for an answer
    
    Available to: Teachers, Admins, Students (their own answers)
    """
    # Get answer
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        session = answer.session
        if session.student_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view suggestions for your own answers"
            )
    elif current_user.role == UserRole.TEACHER:
        session = answer.session
        test = db.query(Test).filter(Test.id == session.test_id).first()
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view suggestions for your own tests"
            )
    
    try:
        service = SessionService(db, use_ai_grading=True)
        suggestions = service.get_improvement_suggestions(answer_id)
        
        return SuggestionsResponse(
            answer_id=answer_id,
            suggestions=suggestions
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/check-plagiarism")
async def check_plagiarism(
    session_id: int,
    threshold: float = 0.8,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check for potential plagiarism in a session
    
    Available to: Teachers, Admins
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot check plagiarism"
        )
    
    # Get session and check ownership
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    test = db.query(Test).filter(Test.id == session.test_id).first()
    
    if current_user.role == UserRole.TEACHER:
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only check plagiarism for your own tests"
            )
    
    try:
        service = SessionService(db, use_ai_grading=True)
        result = service.check_plagiarism(
            session_id=session_id,
            threshold=threshold
        )
        
        return PlagiarismCheckResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tests/{test_id}/ai-stats")
async def get_ai_grading_stats(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics about AI grading for a test
    
    Available to: Teachers, Admins
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot view AI stats"
        )
    
    # Get test and check ownership
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if current_user.role == UserRole.TEACHER:
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view stats for your own tests"
            )
    
    # Get all text answers for this test
    from sqlalchemy import func
    
    stats = (
        db.query(
            func.count(Answer.id).label('total'),
            func.sum(
                func.cast(Answer.answer_data['ai_feedback'].isnot(None), db.Integer)
            ).label('ai_graded'),
            func.sum(
                func.cast(Answer.is_correct == True, db.Integer)
            ).label('correct'),
            func.sum(
                func.cast(Answer.is_correct == False, db.Integer)
            ).label('incorrect'),
            func.sum(
                func.cast(Answer.is_correct.is_(None), db.Integer)
            ).label('manual_review')
        )
        .join(TestSession)
        .join(Question)
        .filter(
            TestSession.test_id == test_id,
            Question.question_type == 'text_input',
            TestSession.status == 'completed'
        )
        .first()
    )
    
    return {
        'test_id': test_id,
        'total_text_answers': stats.total or 0,
        'ai_graded': stats.ai_graded or 0,
        'correct': stats.correct or 0,
        'incorrect': stats.incorrect or 0,
        'manual_review': stats.manual_review or 0,
        'ai_usage_percent': (stats.ai_graded / stats.total * 100) if stats.total > 0 else 0
    }