"""
Модель Prompt (Промпт)
"""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Prompt(Base):
    """Модель промпта из Telegram канала"""

    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    tg_message_id = Column(Integer, unique=True, nullable=False, index=True)
    tg_channel_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=False, index=True)
    is_pinned = Column(Boolean, default=False, nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Связь многие-ко-многим с тегами
    tags = relationship("Tag", secondary="prompt_tags", back_populates="prompts")

    # Индекс для поиска по normalized_text
    __table_args__ = (
        Index("idx_prompt_normalized_text", "normalized_text"),
        Index("idx_prompt_tg_message_id", "tg_message_id", unique=True),
    )

    def __repr__(self):
        text_len = len(self.text) if self.text else 0
        return f"<Prompt(id={self.id}, tg_message_id={self.tg_message_id}, text_length={text_len})>"
