from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from PIL import Image
import io

from ..database import get_db
from ..models.user import User
from ..models.image import Image as ImageModel
from ..utils.security import get_current_user
from ..config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image(file: UploadFile) -> tuple[bool, str]:
    """Валидация загружаемого изображения"""
    # Проверка расширения
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, ""

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузить изображение
    
    Поддерживаемые форматы: JPG, PNG, GIF, WebP
    Максимальный размер: 10MB
    """
    # Валидация
    is_valid, error_msg = validate_image(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Чтение файла
    contents = await file.read()
    
    # Проверка размера
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_SIZE / 1024 / 1024}MB"
        )
    
    # Проверка что это действительно изображение
    try:
        img = Image.open(io.BytesIO(contents))
        width, height = img.size
        img_format = img.format
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )
    
    # Генерация уникального имени
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Сохранение файла
    with open(filepath, 'wb') as f:
        f.write(contents)
    
    # Создание записи в БД
    image = ImageModel(
        filename=unique_filename,
        original_filename=file.filename,
        filepath=filepath,
        mime_type=file.content_type or f"image/{img_format.lower()}",
        file_size=len(contents),
        width=width,
        height=height,
        uploaded_by=current_user.id
    )
    
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return {
        "id": image.id,
        "filename": image.filename,
        "original_filename": image.original_filename,
        "url": f"/uploads/{image.filename}",
        "width": image.width,
        "height": image.height,
        "size": image.file_size
    }

@router.get("/{image_id}")
async def get_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию об изображении"""
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return {
        "id": image.id,
        "filename": image.filename,
        "original_filename": image.original_filename,
        "url": f"/uploads/{image.filename}",
        "width": image.width,
        "height": image.height,
        "size": image.file_size,
        "uploaded_at": image.created_at
    }

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить изображение"""
    image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Проверка прав (только загрузивший может удалить)
    if image.uploaded_by != current_user.id and current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Удаление файла
    try:
        if os.path.exists(image.filepath):
            os.remove(image.filepath)
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Удаление записи из БД
    db.delete(image)
    db.commit()