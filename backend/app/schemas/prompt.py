"""
Pydantic схемы для Prompt
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PromptBase(BaseModel):
    """Базовая схема промпта"""

    tg_message_id: int = Field(..., description="ID сообщения в Telegram")
    tg_channel_id: int = Field(..., description="ID канала в Telegram")
    text: str = Field(..., min_length=1, max_length=10000, description="Текст промпта")
    is_pinned: bool = Field(default=False, description="Закреплен ли промпт")
    image_url: Optional[str] = Field(None, max_length=500, description="URL изображения из Telegram")


class PromptCreate(PromptBase):
    """Схема для создания промпта"""

    pass


class PromptUpdate(BaseModel):
    """Схема для обновления промпта"""

    text: Optional[str] = Field(None, min_length=1, max_length=10000)
    is_pinned: Optional[bool] = None
    image_url: Optional[str] = Field(None, max_length=500)


class TagBase(BaseModel):
    """Базовая схема тега"""

    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)


class TagResponse(TagBase):
    """Схема ответа с тегом"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PromptResponse(PromptBase):
    """Схема ответа с промптом"""

    id: int
    normalized_text: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    """Схема для списка промптов с пагинацией"""

    items: List[PromptResponse]
    total: int
    page: int
    limit: int
