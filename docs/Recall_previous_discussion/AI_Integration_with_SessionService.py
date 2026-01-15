# backend/app/services/session_service.py (Updated with AI)
"""
Updated SessionService with AI grading integration
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from app.models.session import TestSession, Answer
from app.models.test import Question
from app.services.ai_grading_service import AIGradingService


logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, db: Session, use_ai_grading: bool = True):
        self.db = db
        self.use_ai_grading = use_ai_grading
        
        # Initialize AI service
        if use_ai_grading:
            try:
                self.ai_service = AIGradingService()
                if not self.ai_service.enabled:
                    logger.warning("AI grading service not available")
                    self.use_ai_grading = False
            except Exception as e:
                logger.error(f"Failed to initialize AI service: {str(e)}")
                self.use_ai_grading = False
                self.ai_service = None
        else:
            self.ai_service = None
    
    # ... (previous methods remain the same) ...
    
    def _check_text_input(
        self, question: Question, answer: Dict[str, Any]
    ) -> Optional[bool]:
        """
        Check text input answer - NOW WITH AI!
        
        Returns:
            - True: Definitely correct
            - False: Definitely incorrect
            - None: Requires manual grading (uncertain)
        """
        user_text = answer.get("text", "").strip()
        
        if not user_text:
            return False
        
        # Try AI grading if enabled
        if self.use_ai_grading and self.ai_service:
            try:
                result = self.ai_service.grade_text_answer(
                    question=question,
                    student_answer=user_text,
                    use_ai=True,
                    threshold=0.7  # 70% confidence threshold
                )
                
                # Store AI feedback in answer metadata
                answer['ai_feedback'] = {
                    'score': result['score'],
                    'feedback': result['feedback'],
                    'method': result['method'],
                    'matched_keywords': result.get('matched_keywords', []),
                    'suggestions': result.get('suggestions', [])
                }
                
                # Return result based on confidence
                if result['score'] >= 0.85:
                    return True  # High confidence correct
                elif result['score'] <= 0.3:
                    return False  # High confidence incorrect
                else:
                    return None  # Uncertain - needs manual review
                    
            except Exception as e:
                logger.error(f"AI grading failed: {str(e)}")
                # Fall through to keyword matching
        
        # Fallback to keyword matching
        metadata = question.metadata or {}
        keywords = metadata.get("keywords", [])
        
        if keywords:
            user_lower = user_text.lower()
            matched = sum(1 for kw in keywords if kw.lower() in user_lower)
            
            if matched == len(keywords):
                return True
            elif matched >= len(keywords) * 0.7:
                return None  # Partial match - manual review
            else:
                return False
        
        # No evaluation criteria - requires manual grading
        return None
    
    # ==================== NEW METHODS ====================
    
    def get_answer_with_ai_feedback(
        self, answer_id: int
    ) -> Dict[str, Any]:
        """
        Get answer with AI feedback details
        
        Returns:
            {
                'answer': Answer object,
                'ai_feedback': {...} or None,
                'quality_metrics': {...}
            }
        """
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            raise ValueError("Answer not found")
        
        result = {
            'answer': answer,
            'ai_feedback': None,
            'quality_metrics': None
        }
        
        # Get AI feedback if available
        if answer.answer_data and 'ai_feedback' in answer.answer_data:
            result['ai_feedback'] = answer.answer_data['ai_feedback']
        
        # Analyze answer quality
        if answer.question.question_type == 'text_input':
            text = answer.answer_data.get('text', '')
            if text and self.ai_service:
                try:
                    result['quality_metrics'] = self.ai_service.analyze_answer_quality(text)
                except Exception as e:
                    logger.error(f"Failed to analyze answer quality: {str(e)}")
        
        return result
    
    def regrade_text_answer_with_ai(
        self, answer_id: int, use_stricter_threshold: bool = False
    ) -> Dict[str, Any]:
        """
        Re-grade a text answer using AI
        Useful for answers that were initially marked for manual review
        
        Args:
            answer_id: Answer ID
            use_stricter_threshold: Use 0.8 instead of 0.7 threshold
            
        Returns:
            Updated grading result
        """
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            raise ValueError("Answer not found")
        
        question = answer.question
        if question.question_type != 'text_input':
            raise ValueError("Can only re-grade text input questions")
        
        if not self.ai_service:
            raise ValueError("AI grading service not available")
        
        # Get student's text
        student_text = answer.answer_data.get('text', '')
        
        # Re-grade with AI
        threshold = 0.8 if use_stricter_threshold else 0.7
        result = self.ai_service.grade_text_answer(
            question=question,
            student_answer=student_text,
            use_ai=True,
            threshold=threshold
        )
        
        # Update answer
        answer.is_correct = result['is_correct']
        answer.points_earned = question.points if result['is_correct'] else 0
        answer.answer_data['ai_feedback'] = {
            'score': result['score'],
            'feedback': result['feedback'],
            'method': result['method'],
            'matched_keywords': result.get('matched_keywords', []),
            'suggestions': result.get('suggestions', []),
            'regraded': True
        }
        
        self.db.commit()
        self.db.refresh(answer)
        
        return {
            'success': True,
            'is_correct': result['is_correct'],
            'score': result['score'],
            'feedback': result['feedback']
        }
    
    def batch_regrade_text_answers(
        self, session_id: int
    ) -> Dict[str, Any]:
        """
        Re-grade all text answers in a session using AI
        
        Args:
            session_id: Session ID
            
        Returns:
            Summary of regrading results
        """
        if not self.ai_service:
            raise ValueError("AI grading service not available")
        
        # Get all text answers in session
        answers = (
            self.db.query(Answer)
            .join(Question)
            .filter(
                Answer.session_id == session_id,
                Question.question_type == 'text_input'
            )
            .all()
        )
        
        results = {
            'total': len(answers),
            'regraded': 0,
            'changed': 0,
            'improved': 0,
            'declined': 0
        }
        
        for answer in answers:
            try:
                old_correct = answer.is_correct
                
                # Re-grade
                regrade_result = self.regrade_text_answer_with_ai(answer.id)
                results['regraded'] += 1
                
                # Check if result changed
                new_correct = regrade_result['is_correct']
                if old_correct != new_correct:
                    results['changed'] += 1
                    if new_correct and not old_correct:
                        results['improved'] += 1
                    elif not new_correct and old_correct:
                        results['declined'] += 1
                        
            except Exception as e:
                logger.error(f"Failed to regrade answer {answer.id}: {str(e)}")
        
        return results
    
    def get_improvement_suggestions(
        self, answer_id: int
    ) -> List[str]:
        """
        Get AI-powered improvement suggestions for an answer
        
        Args:
            answer_id: Answer ID
            
        Returns:
            List of suggestions
        """
        if not self.ai_service:
            return ["AI suggestions not available"]
        
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            raise ValueError("Answer not found")
        
        question = answer.question
        student_text = answer.answer_data.get('text', '')
        
        metadata = question.metadata or {}
        expected_answers = metadata.get('expected_answers', [])
        
        try:
            suggestions = self.ai_service.suggest_improvements(
                question_text=question.question_text,
                student_answer=student_text,
                expected_answers=expected_answers
            )
            return suggestions
        except Exception as e:
            logger.error(f"Failed to get suggestions: {str(e)}")
            return [f"Error: {str(e)}"]
    
    def check_plagiarism(
        self, session_id: int, threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Check all text answers in a session for potential plagiarism
        
        Args:
            session_id: Session ID
            threshold: Similarity threshold for plagiarism
            
        Returns:
            Report of suspicious answers
        """
        if not self.ai_service:
            raise ValueError("AI service not available")
        
        # Get all text answers in session
        answers = (
            self.db.query(Answer)
            .join(Question)
            .filter(
                Answer.session_id == session_id,
                Question.question_type == 'text_input'
            )
            .all()
        )
        
        # Collect all answers as reference texts
        reference_texts = [ans.answer_data.get('text', '') for ans in answers]
        
        suspicious_answers = []
        
        for i, answer in enumerate(answers):
            student_text = answer.answer_data.get('text', '')
            
            # Compare with other answers (exclude self)
            other_texts = reference_texts[:i] + reference_texts[i+1:]
            
            result = self.ai_service.detect_plagiarism(
                student_answer=student_text,
                reference_texts=other_texts,
                threshold=threshold
            )
            
            if result['is_plagiarized']:
                suspicious_answers.append({
                    'answer_id': answer.id,
                    'question_id': answer.question_id,
                    'similarity': result['max_similarity'],
                    'matched_sources': result['matched_sources']
                })
        
        return {
            'total_checked': len(answers),
            'suspicious_count': len(suspicious_answers),
            'suspicious_answers': suspicious_answers
        }