"""
Pydantic схемы для Tag
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class TagBase(BaseModel):
    """Базовая схема тега"""
    name: str = Field(..., min_length=1, max_length=50, description="Название тега")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация названия тега"""
        if not v.strip():
            raise ValueError("Название тега не может быть пустым")
        return v.strip()


class TagCreate(TagBase):
    """Схема для создания тега"""
    
    @field_validator('name')
    @classmethod
    def generate_slug(cls, v: str) -> str:
        """Генерация slug из названия"""
        # Slug будет генерироваться в сервисе
        return v


class TagUpdate(BaseModel):
    """Схема для обновления тега"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class TagResponse(TagBase):
    """Схема ответа с тегом"""
    id: int
    slug: str
    created_at: datetime
    
    class Config:
        from_attributes = True

