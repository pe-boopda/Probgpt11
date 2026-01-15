# backend/app/models/test.py (Updated with advanced settings)
"""
Updated Test model with advanced settings
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Test(Base):
    __tablename__ = "tests"
    
    # Basic fields
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    passing_score = Column(Float, default=70.0)  # Percentage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ==================== NEW: ADVANCED SETTINGS ====================
    
    # Access Control
    available_from = Column(DateTime, nullable=True)  # Start date/time
    available_until = Column(DateTime, nullable=True)  # End date/time
    access_code = Column(String(50), nullable=True)  # Optional password
    
    # Attempt Limits
    max_attempts = Column(Integer, nullable=True)  # Null = unlimited
    attempt_cooldown = Column(Integer, nullable=True)  # Minutes between attempts
    
    # Time Limits
    time_limit = Column(Integer, nullable=True)  # Minutes (null = no limit)
    show_timer = Column(Boolean, default=True)  # Show countdown timer
    auto_submit_on_timeout = Column(Boolean, default=True)  # Auto-submit when time runs out
    
    # Question Behavior
    shuffle_questions = Column(Boolean, default=False)  # Random order
    shuffle_options = Column(Boolean, default=False)  # Random option order
    one_question_at_time = Column(Boolean, default=False)  # One question per page
    allow_navigation_back = Column(Boolean, default=True)  # Can go back to previous
    
    # Feedback Settings
    show_correct_answers = Column(Boolean, default=False)  # Show after submission
    show_score_immediately = Column(Boolean, default=True)  # Show score after submit
    show_feedback_after = Column(String(20), default="submission")  
    # Options: "never", "submission", "deadline", "manual"
    
    # Advanced Options
    require_webcam = Column(Boolean, default=False)  # Proctoring
    allow_pause = Column(Boolean, default=False)  # Can pause the test
    late_submission_allowed = Column(Boolean, default=False)  # After deadline
    late_submission_penalty = Column(Float, default=0.0)  # Percentage deduction
    
    # IP Restrictions
    allowed_ip_ranges = Column(JSON, nullable=True)  # ["192.168.1.0/24", ...]
    
    # Additional metadata
    settings_metadata = Column(JSON, nullable=True)
    # For future extensibility:
    # {
    #     "require_full_screen": true,
    #     "block_copy_paste": true,
    #     "randomize_seed": 12345,
    #     "custom_instructions": "Use only pencil..."
    # }
    
    # Relationships
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    sessions = relationship("TestSession", back_populates="test")
    creator = relationship("User", back_populates="created_tests")


class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    time_taken = Column(Integer, nullable=True)  # Seconds
    paused_at = Column(DateTime, nullable=True)
    paused_duration = Column(Integer, default=0)  # Total pause time in seconds
    
    # Results
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    
    # ==================== NEW: ADVANCED TRACKING ====================
    
    # Attempt tracking
    attempt_number = Column(Integer, default=1)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Behavioral tracking
    tab_switches = Column(Integer, default=0)  # Left the tab
    full_screen_exits = Column(Integer, default=0)  # Exited fullscreen
    suspicious_activity_count = Column(Integer, default=0)
    
    # Submission
    submitted_late = Column(Boolean, default=False)
    late_penalty_applied = Column(Float, default=0.0)
    submission_notes = Column(Text, nullable=True)
    
    # Session metadata
    session_metadata = Column(JSON, nullable=True)
    # {
    #     "browser": "Chrome 120",
    #     "os": "Windows 10",
    #     "screen_resolution": "1920x1080",
    #     "proctoring_snapshots": ["img1.jpg", "img2.jpg"],
    #     "keystroke_pattern": {...}
    # }
    
    # Relationships
    test = relationship("Test", back_populates="sessions")
    student = relationship("User", back_populates="test_sessions")
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")


# ==================== MIGRATION SQL ====================

"""
-- Add new columns to tests table
ALTER TABLE tests ADD COLUMN available_from TIMESTAMP NULL;
ALTER TABLE tests ADD COLUMN available_until TIMESTAMP NULL;
ALTER TABLE tests ADD COLUMN access_code VARCHAR(50) NULL;
ALTER TABLE tests ADD COLUMN max_attempts INTEGER NULL;
ALTER TABLE tests ADD COLUMN attempt_cooldown INTEGER NULL;
ALTER TABLE tests ADD COLUMN time_limit INTEGER NULL;
ALTER TABLE tests ADD COLUMN show_timer BOOLEAN DEFAULT TRUE;
ALTER TABLE tests ADD COLUMN auto_submit_on_timeout BOOLEAN DEFAULT TRUE;
ALTER TABLE tests ADD COLUMN shuffle_questions BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN shuffle_options BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN one_question_at_time BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN allow_navigation_back BOOLEAN DEFAULT TRUE;
ALTER TABLE tests ADD COLUMN show_correct_answers BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN show_score_immediately BOOLEAN DEFAULT TRUE;
ALTER TABLE tests ADD COLUMN show_feedback_after VARCHAR(20) DEFAULT 'submission';
ALTER TABLE tests ADD COLUMN require_webcam BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN allow_pause BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN late_submission_allowed BOOLEAN DEFAULT FALSE;
ALTER TABLE tests ADD COLUMN late_submission_penalty FLOAT DEFAULT 0.0;
ALTER TABLE tests ADD COLUMN allowed_ip_ranges JSON NULL;
ALTER TABLE tests ADD COLUMN settings_metadata JSON NULL;

-- Add new columns to test_sessions table
ALTER TABLE test_sessions ADD COLUMN attempt_number INTEGER DEFAULT 1;
ALTER TABLE test_sessions ADD COLUMN ip_address VARCHAR(45) NULL;
ALTER TABLE test_sessions ADD COLUMN user_agent VARCHAR(500) NULL;
ALTER TABLE test_sessions ADD COLUMN tab_switches INTEGER DEFAULT 0;
ALTER TABLE test_sessions ADD COLUMN full_screen_exits INTEGER DEFAULT 0;
ALTER TABLE test_sessions ADD COLUMN suspicious_activity_count INTEGER DEFAULT 0;
ALTER TABLE test_sessions ADD COLUMN submitted_late BOOLEAN DEFAULT FALSE;
ALTER TABLE test_sessions ADD COLUMN late_penalty_applied FLOAT DEFAULT 0.0;
ALTER TABLE test_sessions ADD COLUMN submission_notes TEXT NULL;
ALTER TABLE test_sessions ADD COLUMN paused_at TIMESTAMP NULL;
ALTER TABLE test_sessions ADD COLUMN paused_duration INTEGER DEFAULT 0;
ALTER TABLE test_sessions ADD COLUMN session_metadata JSON NULL;

-- Create index for attempt tracking
CREATE INDEX idx_sessions_student_test ON test_sessions(student_id, test_id);
CREATE INDEX idx_sessions_attempt ON test_sessions(test_id, student_id, attempt_number);
"""