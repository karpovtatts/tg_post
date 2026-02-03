"""
API эндпоинты для работы с тегами
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.crud import tag as crud_tag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.core.auth import get_current_user
from app.core.logging_config import get_logger

router = APIRouter(prefix="/tags", tags=["tags"])
logger = get_logger(__name__)


@router.get("/", response_model=List[TagResponse])
async def get_tags(
    skip: int = Query(0, ge=0, description="Пропустить элементов"),
    limit: int = Query(100, ge=1, le=100, description="Количество элементов"),
    db: Session = Depends(get_db)
):
    """Получить список всех тегов"""
    tags = crud_tag.get_tags(db, skip=skip, limit=limit)
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Получить тег по ID"""
    tag = crud_tag.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тег не найден"
        )
    
    return TagResponse.model_validate(tag)


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать новый тег (требует аутентификации)"""
    try:
        db_tag = crud_tag.create_tag(db, tag)
        logger.info(f"Создан тег: {db_tag.id} ({db_tag.name})")
        return TagResponse.model_validate(db_tag)
    except Exception as e:
        logger.error(f"Ошибка при создании тега: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании тега"
        )


@router.patch("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить тег (требует аутентификации)"""
    db_tag = crud_tag.update_tag(db, tag_id, tag_update)
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тег не найден"
        )
    
    logger.info(f"Обновлен тег: {tag_id}")
    return TagResponse.model_validate(db_tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить тег (требует аутентификации)"""
    success = crud_tag.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тег не найден"
        )
    
    logger.info(f"Удален тег: {tag_id}")

