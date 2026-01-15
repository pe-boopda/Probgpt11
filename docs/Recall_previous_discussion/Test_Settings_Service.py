# backend/app/services/test_settings_service.py
"""
Service for managing advanced test settings and access validation
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import ipaddress
import logging

from app.models.test import Test, TestSession
from app.models.user import User
from app.schemas.test_settings import (
    TestAccessValidation,
    TestSettingsUpdate,
    TestSettingsResponse
)


logger = logging.getLogger(__name__)


class TestSettingsService:
    """Service for test settings and access control"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== ACCESS VALIDATION ====================
    
    def validate_test_access(
        self,
        test: Test,
        user: User,
        access_code: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TestAccessValidation:
        """
        Validate if user can access the test
        
        Returns TestAccessValidation with can_access and reason
        """
        # Check if test is published
        if not test.is_published:
            return TestAccessValidation(
                can_access=False,
                reason="Тест ещё не опубликован"
            )
        
        # Check date/time availability
        now = datetime.utcnow()
        
        if test.available_from and now < test.available_from:
            return TestAccessValidation(
                can_access=False,
                reason=f"Тест будет доступен с {test.available_from.strftime('%d.%m.%Y %H:%M')}"
            )
        
        if test.available_until and now > test.available_until:
            # Check if late submission is allowed
            if not test.late_submission_allowed:
                return TestAccessValidation(
                    can_access=False,
                    reason=f"Тест был доступен до {test.available_until.strftime('%d.%m.%Y %H:%M')}"
                )
        
        # Check access code
        if test.access_code:
            if not access_code or access_code != test.access_code:
                return TestAccessValidation(
                    can_access=False,
                    reason="Требуется код доступа",
                    requires_code=True
                )
        
        # Check IP restrictions
        if test.allowed_ip_ranges and ip_address:
            if not self._validate_ip_address(ip_address, test.allowed_ip_ranges):
                return TestAccessValidation(
                    can_access=False,
                    reason="Доступ с вашего IP-адреса запрещён"
                )
        
        # Check attempt limits
        if test.max_attempts:
            attempt_count = self._count_user_attempts(test.id, user.id)
            
            if attempt_count >= test.max_attempts:
                return TestAccessValidation(
                    can_access=False,
                    reason=f"Исчерпан лимит попыток ({test.max_attempts})",
                    remaining_attempts=0
                )
            
            remaining = test.max_attempts - attempt_count
            
            # Check cooldown
            if test.attempt_cooldown and attempt_count > 0:
                last_attempt = self._get_last_attempt(test.id, user.id)
                if last_attempt:
                    cooldown_until = last_attempt.completed_at + timedelta(
                        minutes=test.attempt_cooldown
                    )
                    
                    if now < cooldown_until:
                        return TestAccessValidation(
                            can_access=False,
                            reason=f"Следующая попытка будет доступна через {self._format_time_remaining(cooldown_until - now)}",
                            next_attempt_at=cooldown_until,
                            remaining_attempts=remaining
                        )
            
            # Access granted with remaining attempts info
            return TestAccessValidation(
                can_access=True,
                remaining_attempts=remaining
            )
        
        # All checks passed
        return TestAccessValidation(can_access=True)
    
    def _validate_ip_address(
        self, ip_address: str, allowed_ranges: list
    ) -> bool:
        """Check if IP is in allowed ranges"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for range_str in allowed_ranges:
                network = ipaddress.ip_network(range_str, strict=False)
                if ip in network:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"IP validation error: {str(e)}")
            return False
    
    def _count_user_attempts(self, test_id: int, user_id: int) -> int:
        """Count completed attempts"""
        return (
            self.db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.student_id == user_id,
                TestSession.status == "completed"
            )
            .count()
        )
    
    def _get_last_attempt(
        self, test_id: int, user_id: int
    ) -> Optional[TestSession]:
        """Get user's last completed attempt"""
        return (
            self.db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.student_id == user_id,
                TestSession.status == "completed"
            )
            .order_by(TestSession.completed_at.desc())
            .first()
        )
    
    def _format_time_remaining(self, delta: timedelta) -> str:
        """Format time delta as human-readable string"""
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}ч {minutes}м"
        return f"{minutes}м"
    
    # ==================== TIME TRACKING ====================
    
    def calculate_time_remaining(
        self, session: TestSession, test: Test
    ) -> Optional[int]:
        """
        Calculate remaining time in seconds
        Returns None if no time limit
        """
        if not test.time_limit:
            return None
        
        # Calculate elapsed time
        elapsed = (datetime.utcnow() - session.started_at).total_seconds()
        
        # Subtract pause duration
        elapsed -= session.paused_duration
        
        # Calculate remaining
        total_allowed = test.time_limit * 60  # Convert to seconds
        remaining = total_allowed - elapsed
        
        return max(0, int(remaining))
    
    def check_time_expired(
        self, session: TestSession, test: Test
    ) -> bool:
        """Check if time has expired"""
        remaining = self.calculate_time_remaining(session, test)
        return remaining is not None and remaining <= 0
    
    def handle_pause(self, session: TestSession) -> bool:
        """
        Pause a test session
        Returns True if successful
        """
        if session.paused_at:
            return False  # Already paused
        
        session.paused_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def handle_resume(self, session: TestSession) -> bool:
        """
        Resume a paused test session
        Returns True if successful
        """
        if not session.paused_at:
            return False  # Not paused
        
        # Calculate pause duration
        pause_duration = (datetime.utcnow() - session.paused_at).total_seconds()
        session.paused_duration += int(pause_duration)
        session.paused_at = None
        
        self.db.commit()
        return True
    
    # ==================== LATE SUBMISSION ====================
    
    def calculate_late_penalty(
        self, test: Test, submission_time: datetime
    ) -> float:
        """
        Calculate late submission penalty
        Returns penalty percentage (0.0 if not late)
        """
        if not test.available_until:
            return 0.0
        
        if submission_time <= test.available_until:
            return 0.0
        
        if not test.late_submission_allowed:
            return 100.0  # Full penalty
        
        return test.late_submission_penalty
    
    # ==================== QUESTION SHUFFLING ====================
    
    def get_shuffled_questions(
        self, test: Test, seed: Optional[int] = None
    ) -> list:
        """
        Get questions in shuffled order if enabled
        Uses seed for consistent ordering per session
        """
        questions = sorted(test.questions, key=lambda q: q.order)
        
        if not test.shuffle_questions:
            return questions
        
        # Use seed for reproducible shuffling
        import random
        if seed:
            random.seed(seed)
        
        shuffled = questions.copy()
        random.shuffle(shuffled)
        
        return shuffled
    
    def get_shuffled_options(
        self, question, seed: Optional[int] = None
    ) -> list:
        """
        Get options in shuffled order if enabled
        """
        from app.models.test import Test
        
        # Get test to check shuffle_options setting
        test = self.db.query(Test).filter(Test.id == question.test_id).first()
        
        options = sorted(question.options, key=lambda o: o.order)
        
        if not test or not test.shuffle_options:
            return options
        
        import random
        if seed:
            random.seed(seed)
        
        shuffled = options.copy()
        random.shuffle(shuffled)
        
        return shuffled
    
    # ==================== SETTINGS MANAGEMENT ====================
    
    def update_test_settings(
        self, test_id: int, settings: TestSettingsUpdate
    ) -> Test:
        """Update test settings"""
        test = self.db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise ValueError("Test not found")
        
        # Update fields
        update_data = settings.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(test, field, value)
        
        test.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(test)
        
        return test
    
    def get_test_settings(self, test_id: int) -> TestSettingsResponse:
        """Get all test settings"""
        test = self.db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise ValueError("Test not found")
        
        from app.schemas.test_settings import (
            AccessControlSettings,
            AttemptLimitSettings,
            TimingSettings,
            QuestionBehaviorSettings,
            FeedbackSettings,
            SecuritySettings,
            SubmissionSettings
        )
        
        return TestSettingsResponse(
            test_id=test.id,
            access_control=AccessControlSettings(
                available_from=test.available_from,
                available_until=test.available_until,
                access_code=test.access_code,
                allowed_ip_ranges=test.allowed_ip_ranges
            ),
            attempt_limits=AttemptLimitSettings(
                max_attempts=test.max_attempts,
                attempt_cooldown=test.attempt_cooldown
            ),
            timing=TimingSettings(
                time_limit=test.time_limit,
                show_timer=test.show_timer,
                auto_submit_on_timeout=test.auto_submit_on_timeout
            ),
            question_behavior=QuestionBehaviorSettings(
                shuffle_questions=test.shuffle_questions,
                shuffle_options=test.shuffle_options,
                one_question_at_time=test.one_question_at_time,
                allow_navigation_back=test.allow_navigation_back
            ),
            feedback=FeedbackSettings(
                show_correct_answers=test.show_correct_answers,
                show_score_immediately=test.show_score_immediately,
                show_feedback_after=test.show_feedback_after
            ),
            security=SecuritySettings(
                require_webcam=test.require_webcam,
                allow_pause=test.allow_pause,
                require_full_screen=test.settings_metadata.get('require_full_screen', False) if test.settings_metadata else False,
                block_copy_paste=test.settings_metadata.get('block_copy_paste', False) if test.settings_metadata else False
            ),
            submission=SubmissionSettings(
                late_submission_allowed=test.late_submission_allowed,
                late_submission_penalty=test.late_submission_penalty
            )
        )
    
    def apply_preset(self, test_id: int, preset_name: str) -> Test:
        """Apply a preset configuration"""
        from app.schemas.test_settings import PRESETS
        
        if preset_name not in PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        preset = PRESETS[preset_name]
        return self.update_test_settings(test_id, preset.settings)
    
    # ==================== TRACKING ====================
    
    def track_suspicious_activity(
        self, session_id: int, activity_type: str
    ):
        """Track suspicious activity during test"""
        session = self.db.query(TestSession).filter(
            TestSession.id == session_id
        ).first()
        
        if not session:
            return
        
        if activity_type == "tab_switch":
            session.tab_switches += 1
        elif activity_type == "fullscreen_exit":
            session.full_screen_exits += 1
        
        session.suspicious_activity_count += 1
        
        # Log the activity
        logger.warning(
            f"Suspicious activity in session {session_id}: {activity_type}"
        )
        
        self.db.commit()