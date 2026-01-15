from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from ..models.test import Test
from ..models.question import Question, QuestionOption
from ..models.session import TestSession, SessionStatus
from ..models.user import User
from ..schemas.test import (
    TestCreate,
    TestUpdate,
    QuestionCreate,
    QuestionUpdate,
    TestStatistics
)
import random

class TestService:
    """Сервис для работы с тестами"""
    
    @staticmethod
    def get_tests(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        published_only: bool = False,
        creator_id: Optional[int] = None
    ) -> Tuple[List[Test], int]:
        """Получить список тестов с фильтрацией"""
        query = db.query(Test)
        
        # Фильтр по создателю
        if creator_id:
            query = query.filter(Test.creator_id == creator_id)
        
        # Фильтр по публикации
        if published_only:
            query = query.filter(Test.is_published == True)
        
        # Поиск
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Test.title.ilike(search_term)) | 
                (Test.description.ilike(search_term))
            )
        
        # Подсчёт общего количества
        total = query.count()
        
        # Получение с пагинацией
        tests = query.order_by(Test.created_at.desc()).offset(skip).limit(limit).all()
        
        return tests, total
    
    @staticmethod
    def get_test_by_id(db: Session, test_id: int, include_questions: bool = False) -> Test:
        """Получить тест по ID"""
        query = db.query(Test)
        
        if include_questions:
            from sqlalchemy.orm import joinedload
            query = query.options(
                joinedload(Test.questions).joinedload(Question.options)
            )
        
        test = query.filter(Test.id == test_id).first()
        
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test with id {test_id} not found"
            )
        
        return test
    
    @staticmethod
    def create_test(db: Session, test_data: TestCreate, creator_id: int) -> Test:
        """Создать новый тест"""
        test = Test(
            **test_data.model_dump(),
            creator_id=creator_id
        )
        
        db.add(test)
        db.commit()
        db.refresh(test)
        
        return test
    
    @staticmethod
    def update_test(db: Session, test_id: int, test_data: TestUpdate, user_id: int) -> Test:
        """Обновить тест"""
        test = TestService.get_test_by_id(db, test_id)
        
        # Проверка прав (только создатель может редактировать)
        if test.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this test"
            )
        
        # Обновление полей
        update_data = test_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(test, field, value)
        
        db.commit()
        db.refresh(test)
        
        return test
    
    @staticmethod
    def delete_test(db: Session, test_id: int, user_id: int) -> None:
        """Удалить тест"""
        test = TestService.get_test_by_id(db, test_id)
        
        # Проверка прав
        if test.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this test"
            )
        
        db.delete(test)
        db.commit()
    
    @staticmethod
    def publish_test(db: Session, test_id: int, is_published: bool, user_id: int) -> Test:
        """Опубликовать/снять с публикации тест"""
        test = TestService.get_test_by_id(db, test_id, include_questions=True)
        
        # Проверка прав
        if test.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to publish this test"
            )
        
        # Проверка наличия вопросов при публикации
        if is_published and len(test.questions) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish test without questions"
            )
        
        test.is_published = is_published
        db.commit()
        db.refresh(test)
        
        return test
    
    @staticmethod
    def add_question(db: Session, test_id: int, question_data: QuestionCreate, user_id: int) -> Question:
        """Добавить вопрос к тесту"""
        test = TestService.get_test_by_id(db, test_id)
        
        # Проверка прав
        if test.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to add questions to this test"
            )
        
        # Создание вопроса
        question = Question(
            test_id=test_id,
            question_type=question_data.question_type,
            question_text=question_data.question_text,
            order=question_data.order,
            points=question_data.points,
            image_id=question_data.image_id,
            metadata=question_data.metadata
        )
        
        db.add(question)
        db.flush()  # Получить ID вопроса
        
        # Добавление вариантов ответов
        for option_data in question_data.options:
            option = QuestionOption(
                question_id=question.id,
                **option_data.model_dump()
            )
            db.add(option)
        
        db.commit()
        db.refresh(question)
        
        return question
    
    @staticmethod
    def update_question(
        db: Session,
        question_id: int,
        question_data: QuestionUpdate,
        user_id: int
    ) -> Question:
        """Обновить вопрос"""
        question = db.query(Question).filter(Question.id == question_id).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with id {question_id} not found"
            )
        
        # Проверка прав через тест
        test = TestService.get_test_by_id(db, question.test_id)
        if test.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this question"
            )
        
        # Обновление полей вопроса
        update_data = question_data.model_dump(exclude_unset=True, exclude={'options'})
        for field, value in update_data.items():
            setattr(question, field, value)
        
        # Обновление вариантов ответов, если переданы
        if question_data.options is not None:
            # Удаление старых вариантов
            db.query(QuestionOption).filter(QuestionOption.question_id == question_id).delete()
            
            # Добавление новых вариантов
            for option_data in question_data.options:
                option = QuestionOption(
                    question_id=question_id,
                    **option_data.model_dump()
                )
                db.add(option)
        
        db.commit()
        db.refresh(question)
        
        return question
    
    @staticmethod
    def delete_question(db: Session, question_id: int, user_id: int) -> None:
        """Удалить вопрос"""
        question = db.query(Question).filter(Question.id == question_id).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with id {question_id} not found"
            )
        
        # Проверка прав
        test = TestService.get_test_by_id(db, question.test_id)
        if test.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this question"
            )
        
        db.delete(question)
        db.commit()
    
    @staticmethod
    def get_test_statistics(db: Session, test_id: int) -> TestStatistics:
        """Получить статистику по тесту"""
        test = TestService.get_test_by_id(db, test_id)
        
        # Получение сессий
        sessions = db.query(TestSession).filter(TestSession.test_id == test_id).all()
        
        total_attempts = len(sessions)
        completed = [s for s in sessions if s.status == SessionStatus.COMPLETED]
        completed_count = len(completed)
        
        if completed_count == 0:
            return TestStatistics(
                test_id=test_id,
                total_attempts=total_attempts,
                completed_attempts=0,
                average_score=0,
                pass_rate=0,
                average_time_minutes=0
            )
        
        # Вычисление статистики
        scores = [s.score for s in completed]
        avg_score = sum(scores) / len(scores)
        
        passed = [s for s in completed if s.score >= test.passing_score]
        pass_rate = (len(passed) / completed_count) * 100
        
        # Среднее время прохождения
        times = []
        for s in completed:
            if s.completed_at and s.started_at:
                duration = (s.completed_at - s.started_at).total_seconds() / 60
                times.append(duration)
        
        avg_time = sum(times) / len(times) if times else 0
        
        return TestStatistics(
            test_id=test_id,
            total_attempts=total_attempts,
            completed_attempts=completed_count,
            average_score=round(avg_score, 2),
            pass_rate=round(pass_rate, 2),
            average_time_minutes=round(avg_time, 2)
        )
    
    @staticmethod
    def calculate_test_info(test: Test) -> dict:
        """Вычислить информацию о тесте (количество вопросов, баллы)"""
        questions_count = len(test.questions) if hasattr(test, 'questions') else 0
        total_points = sum(q.points for q in test.questions) if hasattr(test, 'questions') else 0
        
        return {
            'questions_count': questions_count,
            'total_points': total_points
        }