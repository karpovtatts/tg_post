"""
Модель связи Prompt-Tag (многие-ко-многим)
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base


class PromptTag(Base):
    """Связующая таблица для связи промптов и тегов (многие-ко-многим)"""
    
    __tablename__ = "prompt_tags"
    
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
    # Уникальное ограничение на пару (prompt_id, tag_id)
    __table_args__ = (
        UniqueConstraint('prompt_id', 'tag_id', name='uq_prompt_tag'),
    )
    
    def __repr__(self):
        return f"<PromptTag(prompt_id={self.prompt_id}, tag_id={self.tag_id})>"

