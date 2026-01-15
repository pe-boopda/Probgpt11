"""Скрипт для создания администратора"""
import sys
from sqlalchemy.orm import Session
from ..database import SessionLocal, engine, Base
from ..models.user import User, UserRole
from ..utils.security import get_password_hash

def create_admin():
    """Создание администратора"""
    
    # Создание таблиц
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("=== Создание администратора ===\n")
        
        # Ввод данных
        email = input("Email: ").strip()
        username = input("Username: ").strip()
        full_name = input("Full Name: ").strip()
        password = input("Password: ").strip()
        
        # Проверка существования
        if db.query(User).filter(User.email == email).first():
            print(f"\n❌ Пользователь с email {email} уже существует!")
            return
        
        if db.query(User).filter(User.username == username).first():
            print(f"\n❌ Пользователь с username {username} уже существует!")
            return
        
        # Создание администратора
        admin = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"\n✅ Администратор успешно создан!")
        print(f"ID: {admin.id}")
        print(f"Email: {admin.email}")
        print(f"Username: {admin.username}")
        print(f"Role: {admin.role.value}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Операция отменена")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()