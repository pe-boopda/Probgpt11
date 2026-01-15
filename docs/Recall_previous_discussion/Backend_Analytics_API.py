# backend/app/services/analytics_service.py
"""
Advanced analytics service for detailed test analysis
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Dict, Any
from collections import defaultdict, Counter
from datetime import datetime

from app.models.test import Test, Question, QuestionOption
from app.models.session import TestSession, Answer
from app.models.user import User


class AnalyticsService:
    """Service for generating detailed test analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_test_overview(self, test_id: int) -> Dict[str, Any]:
        """
        Get high-level test statistics
        
        Returns:
            {
                'total_students': int,
                'passed_students': int,
                'failed_students': int,
                'avg_score': float,
                'median_score': float,
                'avg_time': int,
                'suspicious_count': int
            }
        """
        sessions = (
            self.db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.status == "completed"
            )
            .all()
        )
        
        if not sessions:
            return {
                'total_students': 0,
                'passed_students': 0,
                'failed_students': 0,
                'avg_score': 0.0,
                'median_score': 0.0,
                'avg_time': 0,
                'suspicious_count': 0
            }
        
        scores = [s.percentage for s in sessions]
        scores.sort()
        
        total = len(sessions)
        passed = sum(1 for s in sessions if s.passed)
        suspicious = sum(1 for s in sessions if s.suspicious_activity_count > 0)
        
        # Calculate median
        mid = total // 2
        if total % 2 == 0:
            median = (scores[mid - 1] + scores[mid]) / 2
        else:
            median = scores[mid]
        
        return {
            'total_students': total,
            'passed_students': passed,
            'failed_students': total - passed,
            'avg_score': sum(scores) / total,
            'median_score': median,
            'avg_time': sum(s.time_taken or 0 for s in sessions) // total,
            'suspicious_count': suspicious
        }
    
    def get_question_analytics(
        self, test_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get detailed analytics for each question
        
        Returns list of:
            {
                'question_id': int,
                'question_text': str,
                'question_type': str,
                'points': float,
                'correct_count': int,
                'incorrect_count': int,
                'unanswered_count': int,
                'percentage': float,
                'difficulty': str,
                'avg_time': int,
                'common_mistakes': [
                    {'answer': str, 'count': int, 'percentage': float}
                ]
            }
        """
        test = self.db.query(Test).filter(Test.id == test_id).first()
        if not test:
            return []
        
        results = []
        
        for question in test.questions:
            # Get all answers for this question
            answers = (
                self.db.query(Answer)
                .join(TestSession)
                .filter(
                    Answer.question_id == question.id,
                    TestSession.status == "completed"
                )
                .all()
            )
            
            if not answers:
                continue
            
            total_answers = len(answers)
            correct = sum(1 for a in answers if a.is_correct)
            incorrect = sum(1 for a in answers if a.is_correct == False)
            unanswered = total_answers - correct - incorrect
            
            percentage = (correct / total_answers * 100) if total_answers > 0 else 0
            
            # Determine difficulty
            if percentage >= 80:
                difficulty = "easy"
            elif percentage >= 50:
                difficulty = "medium"
            else:
                difficulty = "hard"
            
            # Analyze common mistakes
            common_mistakes = self._analyze_common_mistakes(
                question, 
                answers
            )
            
            results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'points': question.points,
                'correct_count': correct,
                'incorrect_count': incorrect,
                'unanswered_count': unanswered,
                'percentage': percentage,
                'difficulty': difficulty,
                'common_mistakes': common_mistakes[:5]  # Top 5
            })
        
        return results
    
    def _analyze_common_mistakes(
        self, 
        question: Question, 
        answers: List[Answer]
    ) -> List[Dict[str, Any]]:
        """Analyze common wrong answers"""
        
        # Get incorrect answers
        incorrect_answers = [
            a for a in answers if a.is_correct == False
        ]
        
        if not incorrect_answers:
            return []
        
        # Count wrong answers by content
        wrong_answer_counts = defaultdict(int)
        
        for answer in incorrect_answers:
            answer_data = answer.answer_data
            
            if question.question_type == 'multiple_choice':
                option_id = answer_data.get('selected_option_id')
                if option_id:
                    option = next(
                        (opt for opt in question.options if opt.id == option_id),
                        None
                    )
                    if option:
                        wrong_answer_counts[option.option_text] += 1
            
            elif question.question_type == 'multiple_select':
                selected_ids = set(answer_data.get('selected_option_ids', []))
                correct_ids = {opt.id for opt in question.options if opt.is_correct}
                
                # Check what was wrong
                missing = correct_ids - selected_ids
                extra = selected_ids - correct_ids
                
                if missing:
                    wrong_answer_counts["Пропущены правильные варианты"] += 1
                if extra:
                    for opt_id in extra:
                        opt = next(
                            (o for o in question.options if o.id == opt_id),
                            None
                        )
                        if opt:
                            wrong_answer_counts[f"Лишний вариант: {opt.option_text}"] += 1
            
            elif question.question_type == 'text_input':
                text = answer_data.get('text', '').strip()
                if text:
                    # Group similar answers
                    text_lower = text.lower()
                    wrong_answer_counts[text_lower] += 1
        
        # Convert to list and sort by count
        mistakes = [
            {
                'answer': answer,
                'count': count,
                'percentage': (count / len(incorrect_answers) * 100)
            }
            for answer, count in wrong_answer_counts.items()
        ]
        
        mistakes.sort(key=lambda x: x['count'], reverse=True)
        
        return mistakes
    
    def get_student_performance_matrix(
        self, test_id: int
    ) -> Dict[str, Any]:
        """
        Get performance matrix showing each student's answer to each question
        
        Returns:
            {
                'questions': [question_ids],
                'students': [
                    {
                        'student_id': int,
                        'name': str,
                        'answers': [
                            {
                                'question_id': int,
                                'correct': bool,
                                'time_spent': int,
                                'answer_preview': str
                            }
                        ]
                    }
                ]
            }
        """
        test = self.db.query(Test).filter(Test.id == test_id).first()
        if not test:
            return {'questions': [], 'students': []}
        
        sessions = (
            self.db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.status == "completed"
            )
            .all()
        )
        
        question_ids = [q.id for q in sorted(test.questions, key=lambda x: x.order)]
        
        students_data = []
        
        for session in sessions:
            student = self.db.query(User).filter(
                User.id == session.student_id
            ).first()
            
            if not student:
                continue
            
            # Get all answers for this session
            answers_dict = {}
            for answer in session.answers:
                answers_dict[answer.question_id] = answer
            
            # Build answer array in question order
            student_answers = []
            for q_id in question_ids:
                if q_id in answers_dict:
                    answer = answers_dict[q_id]
                    question = next(
                        (q for q in test.questions if q.id == q_id),
                        None
                    )
                    
                    student_answers.append({
                        'question_id': q_id,
                        'correct': answer.is_correct,
                        'answer_preview': self._get_answer_preview(
                            answer, 
                            question
                        )
                    })
                else:
                    student_answers.append({
                        'question_id': q_id,
                        'correct': None,
                        'answer_preview': 'Не отвечено'
                    })
            
            students_data.append({
                'student_id': student.id,
                'name': student.full_name,
                'email': student.email,
                'total_score': session.score,
                'percentage': session.percentage,
                'answers': student_answers
            })
        
        return {
            'questions': question_ids,
            'students': students_data
        }
    
    def _get_answer_preview(
        self, answer: Answer, question: Question
    ) -> str:
        """Get short preview of student's answer"""
        data = answer.answer_data
        
        if question.question_type == 'multiple_choice':
            option_id = data.get('selected_option_id')
            if option_id:
                option = next(
                    (opt for opt in question.options if opt.id == option_id),
                    None
                )
                return option.option_text if option else "Unknown"
        
        elif question.question_type == 'text_input':
            text = data.get('text', '')
            return text[:50] + ('...' if len(text) > 50 else '')
        
        elif question.question_type == 'multiple_select':
            count = len(data.get('selected_option_ids', []))
            return f"{count} вариантов"
        
        return "Ответ получен"
    
    def get_time_distribution(
        self, test_id: int
    ) -> Dict[str, Any]:
        """
        Get time spent distribution
        
        Returns:
            {
                'avg_time': int,
                'min_time': int,
                'max_time': int,
                'distribution': [
                    {'range': '0-10', 'count': 5},
                    {'range': '10-20', 'count': 10},
                    ...
                ]
            }
        """
        sessions = (
            self.db.query(TestSession)
            .filter(
                TestSession.test_id == test_id,
                TestSession.status == "completed",
                TestSession.time_taken.isnot(None)
            )
            .all()
        )
        
        if not sessions:
            return {
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'distribution': []
            }
        
        times = [s.time_taken for s in sessions]
        avg_time = sum(times) // len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Create distribution buckets (in minutes)
        buckets = [0, 10, 20, 30, 40, 50, 60, 90, 120]
        distribution = []
        
        for i in range(len(buckets) - 1):
            low = buckets[i] * 60
            high = buckets[i + 1] * 60
            count = sum(1 for t in times if low <= t < high)
            
            if count > 0:
                distribution.append({
                    'range': f"{buckets[i]}-{buckets[i+1]} мин",
                    'count': count
                })
        
        # Add final bucket for anything over
        over_count = sum(1 for t in times if t >= buckets[-1] * 60)
        if over_count > 0:
            distribution.append({
                'range': f"{buckets[-1]}+ мин",
                'count': over_count
            })
        
        return {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'distribution': distribution
        }
    
    def get_insights(self, test_id: int) -> List[Dict[str, Any]]:
        """
        Generate AI-powered insights about the test
        
        Returns list of insights with type and message
        """
        insights = []
        
        # Get analytics
        overview = self.get_test_overview(test_id)
        questions = self.get_question_analytics(test_id)
        
        # Insight 1: Overall performance
        avg_score = overview['avg_score']
        if avg_score >= 80:
            insights.append({
                'type': 'success',
                'title': 'Отличные результаты',
                'message': f'Средний балл теста составляет {avg_score:.1f}%. Студенты показали хорошее понимание материала.'
            })
        elif avg_score < 60:
            insights.append({
                'type': 'warning',
                'title': 'Низкие результаты',
                'message': f'Средний балл теста составляет {avg_score:.1f}%. Рекомендуется пересмотреть методику преподавания или сложность теста.'
            })
        
        # Insight 2: Difficult questions
        hard_questions = [q for q in questions if q['difficulty'] == 'hard']
        if hard_questions:
            q_list = ', '.join([f"#{q['question_id']}" for q in hard_questions[:3]])
            insights.append({
                'type': 'alert',
                'title': 'Сложные вопросы',
                'message': f'Вопросы {q_list} вызвали затруднения у студентов. Рекомендуется провести дополнительное объяснение.'
            })
        
        # Insight 3: Suspicious activity
        if overview['suspicious_count'] > 0:
            percentage = (overview['suspicious_count'] / overview['total_students'] * 100)
            insights.append({
                'type': 'warning',
                'title': 'Подозрительная активность',
                'message': f'{overview["suspicious_count"]} студентов ({percentage:.1f}%) показали подозрительное поведение во время теста.'
            })
        
        # Insight 4: Time analysis
        time_dist = self.get_time_distribution(test_id)
        if time_dist['min_time'] < 600:  # Less than 10 minutes
            insights.append({
                'type': 'warning',
                'title': 'Слишком быстрое выполнение',
                'message': f'Некоторые студенты завершили тест менее чем за {time_dist["min_time"]//60} минут. Возможно случайные ответы.'
            })
        
        return insights