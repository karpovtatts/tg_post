"""
Модель Tag (Тег)
"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tag(Base):
    """Модель тега для категоризации промптов"""
    
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Связь многие-ко-многим с промптами
    prompts = relationship("Prompt", secondary="prompt_tags", back_populates="tags")
    
    # Индекс для поиска по slug
    __table_args__ = (
        Index('idx_tag_slug', 'slug', unique=True),
    )
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, slug={self.slug})>"

