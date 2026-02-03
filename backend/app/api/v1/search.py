"""
API эндпоинт для поиска
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.crud import prompt as crud_prompt
from app.database import get_db
from app.schemas.prompt import PromptListResponse, PromptResponse

router = APIRouter(prefix="/search", tags=["search"])
logger = get_logger(__name__)


@router.get("/", response_model=PromptListResponse)
async def search_prompts(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(50, ge=1, le=100, description="Количество элементов на странице"),
    tags: Optional[List[int]] = Query(None, description="Фильтр по ID тегов"),
    pinned: Optional[bool] = Query(None, description="Только закрепленные"),
    db: Session = Depends(get_db),
):
    """
    Поиск промптов по тексту

    Использует нормализованный текст для поиска
    """
    try:
        skip = (page - 1) * limit
        prompts, total = crud_prompt.get_prompts(
            db=db, skip=skip, limit=limit, search=q, tag_ids=tags, pinned_only=pinned
        )

        return PromptListResponse(
            items=[PromptResponse.model_validate(p) for p in prompts], total=total, page=page, limit=limit
        )
    except Exception as e:
        logger.error(f"Ошибка при поиске промптов: {e}", extra={"error": str(e)})
        raise
