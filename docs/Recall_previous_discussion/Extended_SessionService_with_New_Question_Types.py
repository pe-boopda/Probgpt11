# backend/app/services/session_service.py
"""
Extended Session Service with support for all question types including:
- Hotspot
- Fill Blanks
- Matching
- Ordering
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime
import math
import json

from app.models.session import TestSession, Answer
from app.models.test import Test, Question, QuestionOption
from app.models.user import User
from app.schemas.session import (
    SessionResponse,
    SessionDetailResponse,
    AnswerSubmit,
    SessionResultResponse,
    QuestionResultResponse,
)


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, test_id: int, student_id: int) -> TestSession:
        """Create a new test session"""
        test = self.db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise ValueError("Test not found")

        session = TestSession(
            test_id=test_id,
            student_id=student_id,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session

    def get_active_session(
        self, test_id: int, student_id: int
    ) -> Optional[TestSession]:
        """Get active session for student and test"""
        return (
            self.db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.student_id == student_id,
                TestSession.status == "in_progress",
            )
            .first()
        )

    def get_session(self, session_id: int) -> TestSession:
        """Get session by ID"""
        session = self.db.query(TestSession).filter(
            TestSession.id == session_id
        ).first()
        if not session:
            raise ValueError("Session not found")
        return session

    def submit_answer(
        self, session_id: int, answer_data: AnswerSubmit
    ) -> Dict[str, Any]:
        """Submit or update an answer"""
        session = self.get_session(session_id)
        
        # Check if answer already exists
        existing_answer = (
            self.db.query(Answer)
            .filter(
                Answer.session_id == session_id,
                Answer.question_id == answer_data.question_id,
            )
            .first()
        )

        question = self.db.query(Question).filter(
            Question.id == answer_data.question_id
        ).first()
        
        if not question:
            raise ValueError("Question not found")

        # Check answer correctness
        is_correct = self._check_answer_correctness(question, answer_data)
        points_earned = question.points if is_correct else 0.0

        if existing_answer:
            # Update existing answer
            existing_answer.answer_data = answer_data.answer_data
            existing_answer.is_correct = is_correct
            existing_answer.points_earned = points_earned
            existing_answer.answered_at = datetime.utcnow()
        else:
            # Create new answer
            new_answer = Answer(
                session_id=session_id,
                question_id=answer_data.question_id,
                answer_data=answer_data.answer_data,
                is_correct=is_correct,
                points_earned=points_earned,
                answered_at=datetime.utcnow(),
            )
            self.db.add(new_answer)

        self.db.commit()
        
        return {
            "success": True,
            "is_correct": is_correct,
            "points_earned": points_earned,
        }

    def _check_answer_correctness(
        self, question: Question, answer_data: AnswerSubmit
    ) -> bool:
        """
        Check if answer is correct based on question type
        """
        question_type = question.question_type
        answer = answer_data.answer_data

        if question_type == "multiple_choice":
            return self._check_multiple_choice(question, answer)
        
        elif question_type == "multiple_select":
            return self._check_multiple_select(question, answer)
        
        elif question_type == "true_false":
            return self._check_multiple_choice(question, answer)
        
        elif question_type == "text_input":
            return self._check_text_input(question, answer)
        
        elif question_type == "image_annotation":
            return self._check_image_annotation(question, answer)
        
        elif question_type == "matching":
            return self._check_matching(question, answer)
        
        elif question_type == "ordering":
            return self._check_ordering(question, answer)
        
        elif question_type == "hotspot":
            return self._check_hotspot(question, answer)
        
        elif question_type == "fill_blanks":
            return self._check_fill_blanks(question, answer)
        
        else:
            # Unknown type - requires manual grading
            return None

    # ==================== EXISTING CHECKERS ====================

    def _check_multiple_choice(
        self, question: Question, answer: Dict[str, Any]
    ) -> bool:
        """Check multiple choice answer"""
        selected_id = answer.get("selected_option_id")
        if not selected_id:
            return False

        correct_option = next(
            (opt for opt in question.options if opt.is_correct), None
        )
        
        return correct_option and correct_option.id == selected_id

    def _check_multiple_select(
        self, question: Question, answer: Dict[str, Any]
    ) -> bool:
        """Check multiple select answer"""
        selected_ids = set(answer.get("selected_option_ids", []))
        if not selected_ids:
            return False

        correct_ids = {
            opt.id for opt in question.options if opt.is_correct
        }
        
        return selected_ids == correct_ids

    def _check_text_input(
        self, question: Question, answer: Dict[str, Any]
    ) -> Optional[bool]:
        """
        Check text input - requires manual grading by default
        Can be auto-graded if metadata has exact_match keywords
        """
        user_text = answer.get("text", "").strip().lower()
        
        if not user_text:
            return False

        # Try auto-grading if metadata has keywords
        metadata = question.metadata or {}
        keywords = metadata.get("keywords", [])
        
        if keywords:
            # Check if user text contains all required keywords
            return all(
                keyword.lower() in user_text for keyword in keywords
            )
        
        # Requires manual grading
        return None

    def _check_image_annotation(
        self, question: Question, answer: Dict[str, Any]
    ) -> Optional[bool]:
        """
        Check image annotation - usually requires manual grading
        """
        # This typically needs manual review
        # But we can check if student made any annotations
        annotations = answer.get("annotations", [])
        return None if annotations else False

    # ==================== NEW CHECKERS ====================

    def _check_matching(
        self, question: Question, answer: Dict[str, Any]
    ) -> bool:
        """
        Check matching question
        
        Answer format:
        {
            "matches": {
                "left_1": "right_2",
                "left_2": "right_1",
                ...
            }
        }
        
        Options should have match_id field indicating correct pairs
        """
        user_matches = answer.get("matches", {})
        
        if not user_matches:
            return False

        # Build correct matches from options
        # Options should have match_id like "left_1", "right_1"
        # and metadata indicating correct pairs
        correct_pairs = {}
        
        # Get metadata with correct pairings
        metadata = question.metadata or {}
        correct_mappings = metadata.get("correct_matches", {})
        
        if not correct_mappings:
            # Fallback: try to build from option order
            left_items = [
                opt for opt in question.options 
                if opt.match_id and opt.match_id.startswith("left_")
            ]
            right_items = [
                opt for opt in question.options 
                if opt.match_id and opt.match_id.startswith("right_")
            ]
            
            # Assume same order = correct match
            for i, left in enumerate(left_items):
                if i < len(right_items):
                    correct_pairs[left.match_id] = right_items[i].match_id
        else:
            correct_pairs = correct_mappings

        # Check if user matches are correct
        if len(user_matches) != len(correct_pairs):
            return False

        for left_id, right_id in user_matches.items():
            if correct_pairs.get(left_id) != right_id:
                return False

        return True

    def _check_ordering(
        self, question: Question, answer: Dict[str, Any]
    ) -> bool:
        """
        Check ordering question
        
        Answer format:
        {
            "order": [option_id_1, option_id_2, option_id_3, ...]
        }
        
        Options should be stored in correct order (by 'order' field)
        """
        user_order = answer.get("order", [])
        
        if not user_order:
            return False

        # Get correct order from question options
        correct_order = [
            opt.id 
            for opt in sorted(question.options, key=lambda x: x.order)
        ]

        # Check if orders match
        return user_order == correct_order

    def _check_hotspot(
        self, question: Question, answer: Dict[str, Any]
    ) -> bool:
        """
        Check hotspot question
        
        Answer format:
        {
            "clicks": [
                {"id": 1, "x": 45.5, "y": 60.2, "timestamp": 123456},
                {"id": 2, "x": 78.3, "y": 35.1, "timestamp": 123457}
            ]
        }
        
        Metadata format:
        {
            "correct_areas": [
                {"x": 45, "y": 60, "radius": 5},
                {"x": 78, "y": 35, "radius": 5}
            ],
            "tolerance": 5
        }
        """
        clicks = answer.get("clicks", [])
        
        if not clicks:
            return False

        metadata = question.metadata or {}
        correct_areas = metadata.get("correct_areas", [])
        tolerance = metadata.get("tolerance", 5)

        if not correct_areas:
            return False

        # Check if each correct area has at least one click within tolerance
        matched_areas = 0

        for area in correct_areas:
            area_x = area.get("x", 0)
            area_y = area.get("y", 0)
            area_radius = area.get("radius", tolerance)

            # Check if any click is within this area
            for click in clicks:
                click_x = click.get("x", 0)
                click_y = click.get("y", 0)

                # Calculate Euclidean distance
                distance = math.sqrt(
                    (click_x - area_x) ** 2 + (click_y - area_y) ** 2
                )

                if distance <= area_radius:
                    matched_areas += 1
                    break  # Move to next area

        # All areas must be matched
        return matched_areas == len(correct_areas)

    def _check_fill_blanks(
        self, question: Question, answer: Dict[str, Any]
    ) -> bool:
        """
        Check fill blanks question
        
        Answer format:
        {
            "blanks": {
                "0": "user answer for blank 0",
                "1": "user answer for blank 1",
                "2": "user answer for blank 2"
            }
        }
        
        Metadata format:
        {
            "correct_answers": {
                "0": ["answer1", "alternative1"],
                "1": ["answer2", "alternative2"],
                "2": ["answer3"]
            },
            "case_sensitive": false,
            "exact_match": true
        }
        """
        user_blanks = answer.get("blanks", {})
        
        if not user_blanks:
            return False

        metadata = question.metadata or {}
        correct_answers = metadata.get("correct_answers", {})
        case_sensitive = metadata.get("case_sensitive", False)
        exact_match = metadata.get("exact_match", True)

        if not correct_answers:
            return False

        # Check each blank
        total_blanks = len(correct_answers)
        correct_blanks = 0

        for blank_id, user_answer in user_blanks.items():
            if blank_id not in correct_answers:
                continue

            expected_answers = correct_answers[blank_id]
            
            # Normalize user answer
            user_ans = user_answer.strip()
            if not case_sensitive:
                user_ans = user_ans.lower()

            # Check against all acceptable answers
            for expected in expected_answers:
                exp_ans = expected.strip()
                if not case_sensitive:
                    exp_ans = exp_ans.lower()

                if exact_match:
                    if user_ans == exp_ans:
                        correct_blanks += 1
                        break
                else:
                    # Fuzzy match - check if expected is in user answer
                    if exp_ans in user_ans or user_ans in exp_ans:
                        correct_blanks += 1
                        break

        # All blanks must be correct
        return correct_blanks == total_blanks

    # ==================== SESSION COMPLETION ====================

    def complete_session(self, session_id: int) -> Dict[str, Any]:
        """Complete the test session and calculate final results"""
        session = self.get_session(session_id)
        
        if session.status == "completed":
            raise ValueError("Session is already completed")

        # Calculate results
        answers = self.db.query(Answer).filter(
            Answer.session_id == session_id
        ).all()

        total_score = sum(
            answer.points_earned or 0 for answer in answers
        )
        
        test = self.db.query(Test).filter(Test.id == session.test_id).first()
        max_score = sum(q.points for q in test.questions)

        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        # Update session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.score = total_score
        session.max_score = max_score
        session.percentage = percentage
        session.passed = percentage >= test.passing_score

        # Calculate time taken
        if session.started_at and session.completed_at:
            time_delta = session.completed_at - session.started_at
            session.time_taken = int(time_delta.total_seconds())

        self.db.commit()
        self.db.refresh(session)

        return {
            "success": True,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "passed": session.passed,
        }

    def get_session_result(self, session_id: int) -> SessionResultResponse:
        """
        Get detailed session results including all answers
        
        This should only be accessible to teachers/admins!
        """
        session = self.get_session(session_id)
        
        if session.status != "completed":
            raise ValueError("Session is not completed yet")

        # Get all answers with question details
        answers = (
            self.db.query(Answer)
            .filter(Answer.session_id == session_id)
            .all()
        )

        question_results = []
        for answer in answers:
            question = answer.question
            
            question_result = QuestionResultResponse(
                question_id=question.id,
                question_text=question.question_text,
                question_type=question.question_type,
                points=question.points,
                points_earned=answer.points_earned or 0,
                is_correct=answer.is_correct,
                user_answer=answer.answer_data,
                correct_answer=self._get_correct_answer(question),
            )
            question_results.append(question_result)

        # Get student info
        student = self.db.query(User).filter(
            User.id == session.student_id
        ).first()

        return SessionResultResponse(
            session_id=session.id,
            test_id=session.test_id,
            student={"id": student.id, "name": student.full_name, "email": student.email},
            score=session.score,
            max_score=session.max_score,
            percentage=session.percentage,
            passed=session.passed,
            completed_at=session.completed_at,
            time_taken=session.time_taken,
            questions=question_results,
        )

    def _get_correct_answer(self, question: Question) -> Dict[str, Any]:
        """Get the correct answer for display purposes"""
        if question.question_type in ["multiple_choice", "true_false"]:
            correct_option = next(
                (opt for opt in question.options if opt.is_correct), None
            )
            return {"correct_option_id": correct_option.id if correct_option else None}
        
        elif question.question_type == "multiple_select":
            correct_ids = [opt.id for opt in question.options if opt.is_correct]
            return {"correct_option_ids": correct_ids}
        
        elif question.question_type == "matching":
            metadata = question.metadata or {}
            return {"correct_matches": metadata.get("correct_matches", {})}
        
        elif question.question_type == "ordering":
            correct_order = [
                opt.id for opt in sorted(question.options, key=lambda x: x.order)
            ]
            return {"correct_order": correct_order}
        
        elif question.question_type == "hotspot":
            metadata = question.metadata or {}
            return {"correct_areas": metadata.get("correct_areas", [])}
        
        elif question.question_type == "fill_blanks":
            metadata = question.metadata or {}
            return {"correct_answers": metadata.get("correct_answers", {})}
        
        else:
            return {}

    def get_session_progress(self, session_id: int) -> Dict[str, Any]:
        """Get session progress without revealing correct answers"""
        session = self.get_session(session_id)
        
        test = self.db.query(Test).filter(Test.id == session.test_id).first()
        total_questions = len(test.questions)
        
        answered = self.db.query(Answer).filter(
            Answer.session_id == session_id
        ).count()

        return {
            "session_id": session_id,
            "status": session.status,
            "total_questions": total_questions,
            "answered_questions": answered,
            "progress_percentage": (answered / total_questions * 100) if total_questions > 0 else 0,
            "time_elapsed": session.time_taken,
        }