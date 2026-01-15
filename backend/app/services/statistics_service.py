from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import statistics

from ..models.test import Test
from ..models.question import Question
from ..models.session import TestSession, Answer, SessionStatus
from ..models.user import User, UserRole
from ..models.group import Group

class StatisticsService:
    """Сервис для сбора и анализа статистики"""
    
    @staticmethod
    def get_dashboard_stats(db: Session, user_id: int) -> Dict:
        """Получить общую статистику для дашборда преподавателя"""
        user = db.query(User).filter(User.id == user_id).first()
        
        # Фильтр по создателю (если не админ)
        test_filter = Test.creator_id == user_id if user.role != UserRole.ADMIN else True
        
        # Общее количество тестов
        total_tests = db.query(Test).filter(test_filter).count()
        published_tests = db.query(Test).filter(
            and_(test_filter, Test.is_published == True)
        ).count()
        
        # Студенты
        total_students = db.query(User).filter(
            User.role == UserRole.STUDENT
        ).count()
        
        # Сессии
        total_sessions = db.query(TestSession).join(Test).filter(test_filter).count()
        active_sessions = db.query(TestSession).join(Test).filter(
            and_(
                test_filter,
                TestSession.status == SessionStatus.IN_PROGRESS
            )
        ).count()
        
        # Группы
        total_groups = db.query(Group).count()
        
        # Средний балл
        avg_score_result = db.query(func.avg(TestSession.score)).join(Test).filter(
            and_(
                test_filter,
                TestSession.status == SessionStatus.COMPLETED
            )
        ).scalar()
        average_score = float(avg_score_result) if avg_score_result else 0
        
        # Тесты за месяц
        month_ago = datetime.utcnow() - timedelta(days=30)
        tests_this_month = db.query(Test).filter(
            and_(
                test_filter,
                Test.created_at >= month_ago
            )
        ).count()
        
        return {
            "total_tests": total_tests,
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_groups": total_groups,
            "published_tests": published_tests,
            "active_sessions": active_sessions,
            "average_score": round(average_score, 2),
            "tests_this_month": tests_this_month
        }
    
    @staticmethod
    def get_test_detailed_stats(db: Session, test_id: int) -> Dict:
        """Детальная статистика по тесту"""
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            return None
        
        sessions = db.query(TestSession).filter(
            TestSession.test_id == test_id
        ).all()
        
        if not sessions:
            return {
                "test_id": test_id,
                "test_title": test.title,
                "total_attempts": 0,
                "completed_attempts": 0,
                "in_progress": 0,
                "abandoned": 0,
                "average_score": 0,
                "median_score": 0,
                "min_score": 0,
                "max_score": 0,
                "pass_rate": 0,
                "average_time_minutes": 0,
                "min_time_minutes": 0,
                "max_time_minutes": 0,
                "total_questions": len(test.questions),
                "average_correct_per_student": 0,
                "last_attempt": None,
                "first_attempt": None
            }
        
        # Подсчет по статусам
        completed = [s for s in sessions if s.status == SessionStatus.COMPLETED]
        in_progress = [s for s in sessions if s.status == SessionStatus.IN_PROGRESS]
        abandoned = [s for s in sessions if s.status == SessionStatus.ABANDONED]
        
        # Статистика по баллам
        scores = [s.score for s in completed]
        passed = [s for s in completed if s.score >= test.passing_score]
        
        # Статистика по времени
        times = []
        for s in completed:
            if s.completed_at and s.started_at:
                duration = (s.completed_at - s.started_at).total_seconds() / 60
                times.append(duration)
        
        # Средние правильные ответы
        correct_answers = [s.correct_answers for s in completed]
        
        return {
            "test_id": test_id,
            "test_title": test.title,
            "total_attempts": len(sessions),
            "completed_attempts": len(completed),
            "in_progress": len(in_progress),
            "abandoned": len(abandoned),
            "average_score": round(statistics.mean(scores), 2) if scores else 0,
            "median_score": round(statistics.median(scores), 2) if scores else 0,
            "min_score": round(min(scores), 2) if scores else 0,
            "max_score": round(max(scores), 2) if scores else 0,
            "pass_rate": round(len(passed) / len(completed) * 100, 2) if completed else 0,
            "average_time_minutes": round(statistics.mean(times), 2) if times else 0,
            "min_time_minutes": round(min(times), 2) if times else 0,
            "max_time_minutes": round(max(times), 2) if times else 0,
            "total_questions": len(test.questions),
            "average_correct_per_student": round(statistics.mean(correct_answers), 2) if correct_answers else 0,
            "last_attempt": max([s.started_at for s in sessions]) if sessions else None,
            "first_attempt": min([s.started_at for s in sessions]) if sessions else None
        }
    
    @staticmethod
    def get_question_breakdown(db: Session, test_id: int) -> Dict:
        """Статистика по каждому вопросу теста"""
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            return None
        
        questions_stats = []
        
        for question in test.questions:
            # Получить все ответы на этот вопрос
            answers = db.query(Answer).join(TestSession).filter(
                and_(
                    Answer.question_id == question.id,
                    TestSession.test_id == test_id,
                    TestSession.status == SessionStatus.COMPLETED
                )
            ).all()
            
            total_answers = len(answers)
            correct = len([a for a in answers if a.is_correct == 1])
            incorrect = len([a for a in answers if a.is_correct == 0])
            unanswered = len([a for a in answers if a.is_correct is None])
            
            correct_rate = (correct / total_answers * 100) if total_answers > 0 else 0
            
            # Определение сложности
            if correct_rate >= 80:
                difficulty = "easy"
            elif correct_rate >= 50:
                difficulty = "medium"
            else:
                difficulty = "hard"
            
            questions_stats.append({
                "question_id": question.id,
                "question_text": question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                "question_type": question.question_type.value,
                "points": question.points,
                "total_answers": total_answers,
                "correct_answers": correct,
                "incorrect_answers": incorrect,
                "unanswered": unanswered,
                "correct_rate": round(correct_rate, 2),
                "difficulty": difficulty,
                "average_time_seconds": None  # Можно добавить если трекать время
            })
        
        return {
            "test_id": test_id,
            "questions": questions_stats
        }
    
    @staticmethod
    def get_student_stats(db: Session, student_id: int) -> Dict:
        """Статистика по студенту"""
        student = db.query(User).filter(User.id == student_id).first()
        if not student or student.role != UserRole.STUDENT:
            return None
        
        sessions = db.query(TestSession).filter(
            TestSession.user_id == student_id
        ).all()
        
        completed = [s for s in sessions if s.status == SessionStatus.COMPLETED]
        
        # Статистика
        scores = [s.score for s in completed]
        passed = [s for s in completed if s.score >= s.test.passing_score]
        
        # Время
        total_time = 0
        for s in completed:
            if s.completed_at and s.started_at:
                duration = (s.completed_at - s.started_at).total_seconds() / 60
                total_time += duration
        
        # Последний тест
        last_test = max([s.started_at for s in sessions]) if sessions else None
        
        return {
            "student_id": student_id,
            "student_name": student.full_name,
            "email": student.email,
            "group_name": student.group.name if student.group else None,
            "total_tests_taken": len(sessions),
            "completed_tests": len(completed),
            "average_score": round(statistics.mean(scores), 2) if scores else 0,
            "total_points_earned": sum([s.points_earned for s in completed]),
            "tests_passed": len(passed),
            "tests_failed": len(completed) - len(passed),
            "pass_rate": round(len(passed) / len(completed) * 100, 2) if completed else 0,
            "last_test_date": last_test,
            "total_time_spent_minutes": round(total_time, 2)
        }
    
    @staticmethod
    def get_group_stats(db: Session, group_id: int) -> Dict:
        """Статистика по группе"""
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return None
        
        students = db.query(User).filter(User.group_id == group_id).all()
        
        # Сессии студентов группы
        student_ids = [s.id for s in students]
        sessions = db.query(TestSession).filter(
            TestSession.user_id.in_(student_ids)
        ).all()
        
        completed = [s for s in sessions if s.status == SessionStatus.COMPLETED]
        scores = [s.score for s in completed]
        
        # Лучший и худший студент
        student_scores = {}
        for student in students:
            student_sessions = [s for s in completed if s.user_id == student.id]
            if student_sessions:
                avg = statistics.mean([s.score for s in student_sessions])
                student_scores[student.full_name] = avg
        
        best_student = max(student_scores.items(), key=lambda x: x[1])[0] if student_scores else None
        worst_student = min(student_scores.items(), key=lambda x: x[1])[0] if student_scores else None
        
        return {
            "group_id": group_id,
            "group_name": group.name,
            "total_students": len(students),
            "active_students": len([s for s in students if s.is_active]),
            "total_tests_assigned": len(set([s.test_id for s in sessions])),
            "total_attempts": len(sessions),
            "average_score": round(statistics.mean(scores), 2) if scores else 0,
            "best_student": best_student,
            "worst_student": worst_student,
            "median_score": round(statistics.median(scores), 2) if scores else 0
        }
    
    @staticmethod
    def get_leaderboard(
        db: Session,
        test_id: Optional[int] = None,
        group_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Таблица лидеров"""
        query = db.query(
            User.id,
            User.full_name,
            Group.name.label('group_name'),
            func.avg(TestSession.score).label('avg_score'),
            func.count(TestSession.id).label('tests_completed')
        ).join(
            TestSession, TestSession.user_id == User.id
        ).outerjoin(
            Group, Group.id == User.group_id
        ).filter(
            and_(
                User.role == UserRole.STUDENT,
                TestSession.status == SessionStatus.COMPLETED
            )
        )
        
        # Фильтры
        if test_id:
            query = query.filter(TestSession.test_id == test_id)
        
        if group_id:
            query = query.filter(User.group_id == group_id)
        
        # Группировка и сортировка
        results = query.group_by(
            User.id, User.full_name, Group.name
        ).order_by(
            desc('avg_score')
        ).limit(limit).all()
        
        # Формирование ответа
        leaderboard = []
        for rank, result in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "student_id": result.id,
                "student_name": result.full_name,
                "score": round(float(result.avg_score), 2),
                "tests_completed": result.tests_completed,
                "group_name": result.group_name
            })
        
        return leaderboard
    
    @staticmethod
    def get_performance_trend(
        db: Session,
        test_id: Optional[int] = None,
        group_id: Optional[int] = None,
        period: str = "daily",
        days: int = 30
    ) -> List[Dict]:
        """Тренд успеваемости по дням"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(
            func.date(TestSession.completed_at).label('date'),
            func.avg(TestSession.score).label('avg_score'),
            func.count(TestSession.id).label('count')
        ).filter(
            and_(
                TestSession.status == SessionStatus.COMPLETED,
                TestSession.completed_at >= start_date
            )
        )
        
        if test_id:
            query = query.filter(TestSession.test_id == test_id)
        
        if group_id:
            query = query.join(User).filter(User.group_id == group_id)
        
        results = query.group_by(func.date(TestSession.completed_at)).all()
        
        trend_data = []
        for result in results:
            trend_data.append({
                "date": str(result.date),
                "value": round(float(result.avg_score), 2),
                "count": result.count
            })
        
        return trend_data