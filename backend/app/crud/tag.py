"""
CRUD операции для Tag
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from app.utils.text import generate_slug


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    """Получить тег по ID"""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_slug(db: Session, slug: str) -> Optional[Tag]:
    """Получить тег по slug"""
    return db.query(Tag).filter(Tag.slug == slug).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    """Получить список всех тегов"""
    return db.query(Tag).order_by(Tag.name).offset(skip).limit(limit).all()


def get_tags_with_count(db: Session, skip: int = 0, limit: int = 100) -> List[tuple]:
    """
    Получить список тегов с количеством промптов для каждого

    Returns:
        List[tuple]: Список кортежей (Tag, count)
    """
    from sqlalchemy import func

    from app.models.prompt_tag import PromptTag

    return (
        db.query(Tag, func.count(PromptTag.prompt_id).label("prompt_count"))
        .join(PromptTag, Tag.id == PromptTag.tag_id)
        .group_by(Tag.id)
        .order_by(func.count(PromptTag.prompt_id).desc(), Tag.name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_tag(db: Session, tag: TagCreate) -> Tag:
    """Создать новый тег"""
    slug = generate_slug(tag.name)

    # Проверка на уникальность slug
    existing_tag = get_tag_by_slug(db, slug)
    if existing_tag:
        # Если slug уже существует, добавляем число
        counter = 1
        while existing_tag:
            new_slug = f"{slug}-{counter}"
            existing_tag = get_tag_by_slug(db, new_slug)
            if not existing_tag:
                slug = new_slug
                break
            counter += 1

    db_tag = Tag(name=tag.name, slug=slug)

    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    return db_tag


def update_tag(db: Session, tag_id: int, tag_update: TagUpdate) -> Optional[Tag]:
    """Обновить тег"""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return None

    if tag_update.name is not None:
        db_tag.name = tag_update.name
        # Перегенерировать slug при изменении имени
        db_tag.slug = generate_slug(tag_update.name)

        # Проверка на уникальность нового slug
        existing_tag = get_tag_by_slug(db, db_tag.slug)
        if existing_tag and existing_tag.id != tag_id:
            # Если slug уже существует, добавляем число
            counter = 1
            while existing_tag and existing_tag.id != tag_id:
                new_slug = f"{db_tag.slug}-{counter}"
                existing_tag = get_tag_by_slug(db, new_slug)
                if not existing_tag:
                    db_tag.slug = new_slug
                    break
                counter += 1

    db.commit()
    db.refresh(db_tag)

    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """Удалить тег (каскадное удаление связей через CASCADE)"""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False

    db.delete(db_tag)
    db.commit()

    return True
