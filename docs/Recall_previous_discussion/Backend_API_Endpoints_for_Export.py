# backend/app/api/export.py
"""
API endpoints for exporting test results
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.test import Test
from app.services.export_service import ExportService


router = APIRouter()


@router.get("/tests/{test_id}/export/excel")
async def export_test_to_excel(
    test_id: int,
    include_details: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export test results to Excel file
    
    Available to: Teachers (their tests), Admins (all tests)
    
    Query params:
        - include_details: Include detailed question breakdown
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot export test results"
        )
    
    if current_user.role == UserRole.TEACHER:
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only export results for your own tests"
            )
    
    # Generate Excel file
    try:
        export_service = ExportService(db)
        excel_file = export_service.export_test_results_to_excel(
            test_id=test_id,
            include_details=include_details
        )
        
        # Get test name for filename
        test = db.query(Test).filter(Test.id == test_id).first()
        filename = f"test_results_{test.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Return as downloadable file
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to Excel: {str(e)}"
        )


@router.get("/tests/{test_id}/export/pdf")
async def export_test_to_pdf(
    test_id: int,
    include_details: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export test results to PDF file
    
    Available to: Teachers (their tests), Admins (all tests)
    
    Query params:
        - include_details: Include detailed question breakdown
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot export test results"
        )
    
    if current_user.role == UserRole.TEACHER:
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only export results for your own tests"
            )
    
    # Generate PDF file
    try:
        export_service = ExportService(db)
        pdf_file = export_service.export_test_results_to_pdf(
            test_id=test_id,
            include_details=include_details
        )
        
        # Get test name for filename
        test = db.query(Test).filter(Test.id == test_id).first()
        filename = f"test_results_{test.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Return as downloadable file
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to PDF: {str(e)}"
        )


@router.get("/sessions/{session_id}/certificate/pdf")
async def export_student_certificate(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export individual student certificate as PDF
    
    Available to:
        - Teachers (for their tests)
        - Admins (for all tests)
        - Students (their own certificates, only if passed)
    """
    export_service = ExportService(db)
    session = export_service.session_service.get_session(session_id)
    
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        # Students can only download their own certificates if passed
        if session.student_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only download your own certificate"
            )
        if not session.passed:
            raise HTTPException(
                status_code=403,
                detail="Certificate is only available for passed tests"
            )
    
    elif current_user.role == UserRole.TEACHER:
        # Teachers can download certificates for their tests
        test = db.query(Test).filter(Test.id == session.test_id).first()
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only generate certificates for your own tests"
            )
    
    # Generate certificate
    try:
        pdf_file = export_service.export_student_certificate_pdf(session_id)
        
        # Get student and test info for filename
        student = db.query(User).filter(User.id == session.student_id).first()
        test = db.query(Test).filter(Test.id == session.test_id).first()
        filename = f"certificate_{student.full_name}_{test.title}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate certificate: {str(e)}"
        )


@router.get("/tests/{test_id}/export/csv")
async def export_test_to_csv(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export test results to CSV file (simple format)
    
    Available to: Teachers (their tests), Admins (all tests)
    """
    # Check permissions
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students cannot export test results"
        )
    
    if current_user.role == UserRole.TEACHER:
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        if test.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only export results for your own tests"
            )
    
    # Generate CSV
    from app.models.session import TestSession
    import csv
    from io import StringIO
    
    sessions = (
        db.query(TestSession)
        .filter(
            TestSession.test_id == test_id,
            TestSession.status == "completed"
        )
        .all()
    )
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Student Name',
        'Email',
        'Completion Date',
        'Time (minutes)',
        'Score',
        'Max Score',
        'Percentage',
        'Passed'
    ])
    
    # Data
    for session in sessions:
        student = db.query(User).filter(User.id == session.student_id).first()
        writer.writerow([
            student.full_name if student else "Unknown",
            student.email if student else "",
            session.completed_at.strftime('%Y-%m-%d %H:%M:%S'),
            session.time_taken // 60 if session.time_taken else 0,
            session.score,
            session.max_score,
            f"{session.percentage:.1f}",
            "Yes" if session.passed else "No"
        ])
    
    # Get test name for filename
    test = db.query(Test).filter(Test.id == test_id).first()
    filename = f"test_results_{test.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Return CSV
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )