# backend/app/schemas/test_settings.py
"""
Pydantic schemas for advanced test settings
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FeedbackTimingEnum(str, Enum):
    """When to show feedback to students"""
    NEVER = "never"
    SUBMISSION = "submission"  # Right after submission
    DEADLINE = "deadline"  # After test deadline
    MANUAL = "manual"  # When teacher manually releases


class AccessControlSettings(BaseModel):
    """Access control settings"""
    available_from: Optional[datetime] = Field(None, description="Test available from")
    available_until: Optional[datetime] = Field(None, description="Test available until")
    access_code: Optional[str] = Field(None, max_length=50, description="Password to access test")
    allowed_ip_ranges: Optional[List[str]] = Field(None, description="Allowed IP ranges (CIDR notation)")
    
    @validator('available_until')
    def validate_date_range(cls, v, values):
        if v and 'available_from' in values and values['available_from']:
            if v <= values['available_from']:
                raise ValueError('available_until must be after available_from')
        return v


class AttemptLimitSettings(BaseModel):
    """Attempt limit settings"""
    max_attempts: Optional[int] = Field(None, ge=1, le=100, description="Max attempts (null = unlimited)")
    attempt_cooldown: Optional[int] = Field(None, ge=0, description="Minutes between attempts")


class TimingSettings(BaseModel):
    """Time limit settings"""
    time_limit: Optional[int] = Field(None, ge=1, description="Time limit in minutes")
    show_timer: bool = Field(True, description="Show countdown timer")
    auto_submit_on_timeout: bool = Field(True, description="Auto-submit when time runs out")


class QuestionBehaviorSettings(BaseModel):
    """Question display behavior"""
    shuffle_questions: bool = Field(False, description="Randomize question order")
    shuffle_options: bool = Field(False, description="Randomize option order")
    one_question_at_time: bool = Field(False, description="One question per page")
    allow_navigation_back: bool = Field(True, description="Allow going back to previous questions")


class FeedbackSettings(BaseModel):
    """Feedback and results settings"""
    show_correct_answers: bool = Field(False, description="Show correct answers after submission")
    show_score_immediately: bool = Field(True, description="Show score after submission")
    show_feedback_after: FeedbackTimingEnum = Field(
        FeedbackTimingEnum.SUBMISSION, 
        description="When to show detailed feedback"
    )


class SecuritySettings(BaseModel):
    """Security and proctoring settings"""
    require_webcam: bool = Field(False, description="Require webcam for proctoring")
    allow_pause: bool = Field(False, description="Allow pausing the test")
    require_full_screen: bool = Field(False, description="Require full screen mode")
    block_copy_paste: bool = Field(False, description="Block copy/paste")


class SubmissionSettings(BaseModel):
    """Submission settings"""
    late_submission_allowed: bool = Field(False, description="Allow submission after deadline")
    late_submission_penalty: float = Field(
        0.0, 
        ge=0.0, 
        le=100.0, 
        description="Penalty percentage for late submission"
    )


class TestSettingsUpdate(BaseModel):
    """Complete test settings for update"""
    # Access Control
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    access_code: Optional[str] = None
    allowed_ip_ranges: Optional[List[str]] = None
    
    # Attempts
    max_attempts: Optional[int] = None
    attempt_cooldown: Optional[int] = None
    
    # Timing
    time_limit: Optional[int] = None
    show_timer: Optional[bool] = None
    auto_submit_on_timeout: Optional[bool] = None
    
    # Question Behavior
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    one_question_at_time: Optional[bool] = None
    allow_navigation_back: Optional[bool] = None
    
    # Feedback
    show_correct_answers: Optional[bool] = None
    show_score_immediately: Optional[bool] = None
    show_feedback_after: Optional[FeedbackTimingEnum] = None
    
    # Security
    require_webcam: Optional[bool] = None
    allow_pause: Optional[bool] = None
    
    # Submission
    late_submission_allowed: Optional[bool] = None
    late_submission_penalty: Optional[float] = None
    
    # Metadata
    settings_metadata: Optional[dict] = None


class TestSettingsResponse(BaseModel):
    """Response with all test settings"""
    test_id: int
    
    # Access Control
    access_control: AccessControlSettings
    
    # Attempts
    attempt_limits: AttemptLimitSettings
    
    # Timing
    timing: TimingSettings
    
    # Question Behavior
    question_behavior: QuestionBehaviorSettings
    
    # Feedback
    feedback: FeedbackSettings
    
    # Security
    security: SecuritySettings
    
    # Submission
    submission: SubmissionSettings
    
    class Config:
        from_attributes = True


class TestAccessValidation(BaseModel):
    """Result of access validation"""
    can_access: bool
    reason: Optional[str] = None
    remaining_attempts: Optional[int] = None
    next_attempt_at: Optional[datetime] = None
    requires_code: bool = False


class SessionTrackingUpdate(BaseModel):
    """Update session tracking metrics"""
    tab_switches: Optional[int] = None
    full_screen_exits: Optional[int] = None
    suspicious_activity_count: Optional[int] = None


class TestPreset(BaseModel):
    """Preset configurations for common test types"""
    name: str
    description: str
    settings: TestSettingsUpdate


# ==================== PRESET CONFIGURATIONS ====================

PRESET_QUIZ = TestPreset(
    name="Быстрый опрос",
    description="Короткий опрос без ограничений",
    settings=TestSettingsUpdate(
        time_limit=10,
        max_attempts=None,
        shuffle_questions=False,
        show_correct_answers=True,
        show_score_immediately=True,
        show_feedback_after=FeedbackTimingEnum.SUBMISSION
    )
)

PRESET_EXAM = TestPreset(
    name="Экзамен",
    description="Строгий экзамен с одной попыткой",
    settings=TestSettingsUpdate(
        time_limit=90,
        max_attempts=1,
        shuffle_questions=True,
        shuffle_options=True,
        one_question_at_time=True,
        allow_navigation_back=False,
        show_correct_answers=False,
        show_score_immediately=False,
        show_feedback_after=FeedbackTimingEnum.MANUAL,
        require_webcam=True,
        allow_pause=False,
        late_submission_allowed=False
    )
)

PRESET_PRACTICE = TestPreset(
    name="Тренировка",
    description="Неограниченная практика с обратной связью",
    settings=TestSettingsUpdate(
        time_limit=None,
        max_attempts=None,
        shuffle_questions=True,
        show_correct_answers=True,
        show_score_immediately=True,
        show_feedback_after=FeedbackTimingEnum.SUBMISSION,
        allow_pause=True
    )
)

PRESET_HOMEWORK = TestPreset(
    name="Домашнее задание",
    description="Задание с дедлайном и несколькими попытками",
    settings=TestSettingsUpdate(
        time_limit=60,
        max_attempts=3,
        attempt_cooldown=60,  # 1 hour
        shuffle_questions=False,
        show_correct_answers=False,
        show_score_immediately=True,
        show_feedback_after=FeedbackTimingEnum.DEADLINE,
        late_submission_allowed=True,
        late_submission_penalty=10.0,
        allow_pause=True
    )
)

PRESET_TIMED_TEST = TestPreset(
    name="Контрольная на время",
    description="Тест с жёстким ограничением времени",
    settings=TestSettingsUpdate(
        time_limit=45,
        show_timer=True,
        auto_submit_on_timeout=True,
        max_attempts=1,
        shuffle_questions=True,
        one_question_at_time=False,
        allow_navigation_back=True,
        show_correct_answers=False,
        show_feedback_after=FeedbackTimingEnum.DEADLINE,
        allow_pause=False
    )
)

# Dict of all presets
PRESETS = {
    "quiz": PRESET_QUIZ,
    "exam": PRESET_EXAM,
    "practice": PRESET_PRACTICE,
    "homework": PRESET_HOMEWORK,
    "timed": PRESET_TIMED_TEST,
}