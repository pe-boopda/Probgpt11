from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Image(Base):
    """Модель изображения"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # В байтах
    
    # Размеры изображения
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Кто загрузил
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Image(id={self.id}, filename={self.filename})>"