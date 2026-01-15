from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import random
import json

from ..models.test import Test
from ..models.question import Question, QuestionOption, QuestionType
from ..models.session import TestSession, Answer, SessionStatus
from ..models.user import User

class SessionService:
    """Сервис для работы с сессиями тестирования"""
    
    @staticmethod
    def start_test(db: Session, test_id: int, user_id: int) -> TestSession:
        """Начать прохождение теста"""
        # Проверка теста
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        if not test.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test is not published"
            )
        
        # Проверка активных сессий
        active_session = db.query(TestSession).filter(
            and_(
                TestSession.test_id == test_id,
                TestSession.user_id == user_id,
                TestSession.status == SessionStatus.IN_PROGRESS
            )
        ).first()
        
        if active_session:
            # Возвращаем существующую сессию
            return active_session
        
        # Получение вопросов
        questions = db.query(Question).filter(
            Question.test_id == test_id
        ).order_by(Question.order).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test has no questions"
            )
        
        # Создание сессии
        session = TestSession(
            test_id=test_id,
            user_id=user_id,
            status=SessionStatus.IN_PROGRESS,
            total_questions=len(questions),
            answered_questions=0,
            correct_answers=0,
            score=0.0,
            points_earned=0.0,
            max_points=sum(q.points for q in questions),
            metadata={
                'question_order': [q.id for q in questions],
                'started_timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Перемешивание вопросов если нужно
        if test.shuffle_questions:
            question_ids = [q.id for q in questions]
            random.shuffle(question_ids)
            session.metadata['question_order'] = question_ids
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: int, user_id: int) -> TestSession:
        """Получить сессию"""
        session = db.query(TestSession).filter(
            TestSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Проверка прав доступа
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return session
    
    @staticmethod
    def get_test_for_session(
        db: Session,
        session: TestSession,
        shuffle_options: bool = False
    ) -> dict:
        """Получить вопросы теста для студента"""
        test = session.test
        
        # Получение порядка вопросов из метаданных
        question_order = session.metadata.get('question_order', [])
        
        # Получение вопросов
        questions = db.query(Question).filter(
            Question.test_id == session.test_id
        ).all()
        
        # Сортировка по сохраненному порядку
        questions_dict = {q.id: q for q in questions}
        ordered_questions = [questions_dict[qid] for qid in question_order if qid in questions_dict]
        
        # Формирование вопросов для студента (без правильных ответов)
        student_questions = []
        for q in ordered_questions:
            options = []
            if q.options:
                option_list = list(q.options)
                
                # Перемешивание опций если нужно
                if shuffle_options:
                    random.shuffle(option_list)
                
                # Убираем информацию о правильности
                options = [
                    {
                        'id': opt.id,
                        'option_text': opt.option_text,
                        'order': idx
                    }
                    for idx, opt in enumerate(option_list)
                ]
            
            student_questions.append({
                'id': q.id,
                'question_type': q.question_type.value,
                'question_text': q.question_text,
                'points': q.points,
                'image_id': q.image_id,
                'order': len(student_questions),
                'options': options,
                'metadata': q.metadata
            })
        
        return {
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'time_limit': test.time_limit,
            'passing_score': test.passing_score,
            'total_questions': len(student_questions),
            'total_points': session.max_points,
            'shuffle_questions': test.shuffle_questions,
            'shuffle_options': test.shuffle_options,
            'questions': student_questions
        }
    
    @staticmethod
    def submit_answer(
        db: Session,
        session_id: int,
        question_id: int,
        answer_data: any,
        user_id: int
    ) -> Answer:
        """Отправить ответ на вопрос"""
        session = SessionService.get_session(db, session_id, user_id)
        
        # Проверка статуса сессии
        if session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not active"
            )
        
        # Проверка времени
        if session.test.time_limit:
            elapsed = (datetime.utcnow() - session.started_at).total_seconds() / 60
            if elapsed > session.test.time_limit:
                # Автоматическое завершение по таймауту
                session.status = SessionStatus.TIMEOUT
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Time limit exceeded"
                )
        
        # Проверка вопроса
        question = db.query(Question).filter(
            and_(
                Question.id == question_id,
                Question.test_id == session.test_id
            )
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Проверка существующего ответа
        existing = db.query(Answer).filter(
            and_(
                Answer.session_id == session_id,
                Answer.question_id == question_id
            )
        ).first()
        
        if existing:
            # Обновление существующего ответа
            existing.answer_data = answer_data
            existing.answered_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Создание нового ответа
        answer = Answer(
            session_id=session_id,
            question_id=question_id,
            answer_data=answer_data
        )
        
        db.add(answer)
        
        # Обновление счетчика отвеченных вопросов
        answered_count = db.query(Answer).filter(
            Answer.session_id == session_id
        ).count()
        session.answered_questions = answered_count + 1
        
        db.commit()
        db.refresh(answer)
        
        return answer
    
    @staticmethod
    def check_answer(question: Question, answer_data: any) -> Tuple[bool, float]:
        """Проверить правильность ответа"""
        q_type = question.question_type
        
        if q_type == QuestionType.MULTIPLE_CHOICE:
            # Один правильный ответ
            correct_id = next((opt.id for opt in question.options if opt.is_correct), None)
            selected_id = answer_data.get('selected_option_id')
            is_correct = correct_id == selected_id
            points = question.points if is_correct else 0
            return is_correct, points
        
        elif q_type == QuestionType.MULTIPLE_SELECT:
            # Несколько правильных ответов
            correct_ids = {opt.id for opt in question.options if opt.is_correct}
            selected_ids = set(answer_data.get('selected_option_ids', []))
            is_correct = correct_ids == selected_ids
            points = question.points if is_correct else 0
            return is_correct, points
        
        elif q_type == QuestionType.TRUE_FALSE:
            # Правда/Ложь
            correct_id = next((opt.id for opt in question.options if opt.is_correct), None)
            selected_id = answer_data.get('selected_option_id')
            is_correct = correct_id == selected_id
            points = question.points if is_correct else 0
            return is_correct, points
        
        elif q_type == QuestionType.TEXT_INPUT:
            # Текстовый ответ - требует ручной проверки
            return None, 0
        
        # Остальные типы требуют специальной обработки
        return None, 0
    
    @staticmethod
    def submit_test(db: Session, session_id: int, user_id: int) -> dict:
        """Завершить тест и вычислить результаты"""
        session = SessionService.get_session(db, session_id, user_id)
        
        if session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not active"
            )
        
        # Получение всех ответов
        answers = db.query(Answer).filter(
            Answer.session_id == session_id
        ).all()
        
        # Проверка ответов
        correct_count = 0
        total_points = 0.0
        
        for answer in answers:
            question = answer.question
            is_correct, points = SessionService.check_answer(question, answer.answer_data)
            
            if is_correct is not None:
                answer.is_correct = 1 if is_correct else 0
                answer.points_awarded = points
                
                if is_correct:
                    correct_count += 1
                total_points += points
        
        # Обновление сессии
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.correct_answers = correct_count
        session.points_earned = total_points
        session.score = (correct_count / session.total_questions * 100) if session.total_questions > 0 else 0
        
        db.commit()
        db.refresh(session)
        
        # Формирование результатов
        return SessionService.get_result(db, session_id, user_id)
    
    @staticmethod
    def get_result(db: Session, session_id: int, user_id: int) -> dict:
        """Получить результаты теста"""
        session = SessionService.get_session(db, session_id, user_id)
        test = session.test
        
        if session.status == SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test is not completed yet"
            )
        
        # Базовые результаты
        time_taken = None
        if session.completed_at:
            time_taken = (session.completed_at - session.started_at).total_seconds() / 60
        
        result = {
            'session_id': session.id,
            'test_title': test.title,
            'status': session.status.value,
            'started_at': session.started_at,
            'completed_at': session.completed_at,
            'time_taken_minutes': round(time_taken, 2) if time_taken else None,
            'total_questions': session.total_questions,
            'answered_questions': session.answered_questions,
            'correct_answers': session.correct_answers,
            'score': round(session.score, 2),
            'points_earned': session.points_earned,
            'max_points': session.max_points,
            'passed': session.score >= test.passing_score,
            'questions_details': None
        }
        
        # Детали по вопросам (если разрешено показывать результаты)
        if test.show_results:
            answers = db.query(Answer).filter(
                Answer.session_id == session_id
            ).all()
            
            questions_details = []
            for answer in answers:
                question = answer.question
                
                # Правильные ответы
                correct_options = [opt.id for opt in question.options if opt.is_correct]
                
                questions_details.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'question_type': question.question_type.value,
                    'points': question.points,
                    'your_answer': answer.answer_data,
                    'correct_answer': correct_options if correct_options else None,
                    'is_correct': bool(answer.is_correct) if answer.is_correct is not None else None,
                    'points_awarded': answer.points_awarded
                })
            
            result['questions_details'] = questions_details
        
        return result
    
    @staticmethod
    def get_time_remaining(session: TestSession) -> Optional[int]:
        """Получить оставшееся время в секундах"""
        if not session.test.time_limit:
            return None
        
        elapsed = (datetime.utcnow() - session.started_at).total_seconds()
        total_seconds = session.test.time_limit * 60
        remaining = int(total_seconds - elapsed)
        
        return max(0, remaining)