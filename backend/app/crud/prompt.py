"""
CRUD операции для Prompt
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime

from app.models.prompt import Prompt
from app.models.tag import Tag
from app.schemas.prompt import PromptCreate, PromptUpdate
from app.utils.text import normalize_text
from app.search.fts5 import search_fts5, search_fallback
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def get_prompt(db: Session, prompt_id: int) -> Optional[Prompt]:
    """Получить промпт по ID (без удаленных)"""
    return db.query(Prompt).filter(
        and_(
            Prompt.id == prompt_id,
            Prompt.deleted_at.is_(None)
        )
    ).first()


def get_prompt_by_tg_message_id(db: Session, tg_message_id: int) -> Optional[Prompt]:
    """Получить промпт по Telegram message ID"""
    return db.query(Prompt).filter(Prompt.tg_message_id == tg_message_id).first()


def get_prompts(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    tag_ids: Optional[List[int]] = None,
    pinned_only: Optional[bool] = None,
    use_fts5: bool = True
) -> tuple[List[Prompt], int]:
    """
    Получить список промптов с фильтрацией и пагинацией
    
    Если указан поисковый запрос, использует FTS5 для полнотекстового поиска.
    Иначе использует обычный запрос.
    
    Args:
        db: Сессия БД
        skip: Пропустить результатов
        limit: Максимум результатов
        search: Поисковый запрос
        tag_ids: Фильтр по ID тегов
        pinned_only: Только закрепленные
        use_fts5: Использовать FTS5 для поиска (если доступно)
        
    Returns:
        tuple: (список промптов, общее количество)
    """
    # Если есть поисковый запрос, используем FTS5
    if search and use_fts5:
        try:
            return search_fts5(
                db=db,
                query=search,
                skip=skip,
                limit=limit,
                tag_ids=tag_ids,
                pinned_only=pinned_only
            )
        except Exception as e:
            logger.warning(f"Ошибка FTS5 поиска, используем fallback: {e}", extra={"error": str(e)})
            # Fallback на обычный поиск
            return search_fallback(
                db=db,
                query=search,
                skip=skip,
                limit=limit,
                tag_ids=tag_ids,
                pinned_only=pinned_only
            )
    elif search:
        # Используем fallback поиск
        return search_fallback(
            db=db,
            query=search,
            skip=skip,
            limit=limit,
            tag_ids=tag_ids,
            pinned_only=pinned_only
        )
    
    # Обычный запрос без поиска
    query = db.query(Prompt).filter(Prompt.deleted_at.is_(None))
    
    # Фильтр по тегам
    if tag_ids:
        query = query.join(Prompt.tags).filter(Tag.id.in_(tag_ids))
    
    # Фильтр по закрепленным
    if pinned_only is not None:
        query = query.filter(Prompt.is_pinned == pinned_only)
    
    # Подсчет общего количества
    total = query.count()
    
    # Сортировка: сначала закрепленные, потом по дате создания (новые первые)
    query = query.order_by(Prompt.is_pinned.desc(), Prompt.created_at.desc())
    
    # Пагинация
    prompts = query.offset(skip).limit(limit).all()
    
    return prompts, total


def create_prompt(db: Session, prompt: PromptCreate) -> Prompt:
    """Создать новый промпт"""
    normalized = normalize_text(prompt.text)
    
    db_prompt = Prompt(
        tg_message_id=prompt.tg_message_id,
        tg_channel_id=prompt.tg_channel_id,
        text=prompt.text,
        normalized_text=normalized,
        is_pinned=prompt.is_pinned
    )
    
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    
    return db_prompt


def update_prompt(db: Session, prompt_id: int, prompt_update: PromptUpdate) -> Optional[Prompt]:
    """Обновить промпт"""
    db_prompt = get_prompt(db, prompt_id)
    if not db_prompt:
        return None
    
    if prompt_update.text is not None:
        db_prompt.text = prompt_update.text
        db_prompt.normalized_text = normalize_text(prompt_update.text)
    
    if prompt_update.is_pinned is not None:
        db_prompt.is_pinned = prompt_update.is_pinned
    
    db.commit()
    db.refresh(db_prompt)
    
    return db_prompt


def delete_prompt(db: Session, prompt_id: int) -> bool:
    """Мягкое удаление промпта"""
    db_prompt = get_prompt(db, prompt_id)
    if not db_prompt:
        return False
    
    db_prompt.deleted_at = datetime.utcnow()
    db.commit()
    
    return True


def pin_prompt(db: Session, prompt_id: int, pin: bool) -> Optional[Prompt]:
    """Закрепить/открепить промпт"""
    db_prompt = get_prompt(db, prompt_id)
    if not db_prompt:
        return None
    
    db_prompt.is_pinned = pin
    db.commit()
    db.refresh(db_prompt)
    
    return db_prompt


def add_tag_to_prompt(db: Session, prompt_id: int, tag_id: int) -> Optional[Prompt]:
    """Добавить тег к промпту"""
    db_prompt = get_prompt(db, prompt_id)
    if not db_prompt:
        return None
    
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        return None
    
    if db_tag not in db_prompt.tags:
        db_prompt.tags.append(db_tag)
        db.commit()
        db.refresh(db_prompt)
    
    return db_prompt


def remove_tag_from_prompt(db: Session, prompt_id: int, tag_id: int) -> Optional[Prompt]:
    """Удалить тег из промпта"""
    db_prompt = get_prompt(db, prompt_id)
    if not db_prompt:
        return None
    
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag and db_tag in db_prompt.tags:
        db_prompt.tags.remove(db_tag)
        db.commit()
        db.refresh(db_prompt)
    
    return db_prompt

