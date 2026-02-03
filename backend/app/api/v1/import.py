"""
API эндпоинт для импорта промптов
"""

from typing import List

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.logging_config import get_logger
from app.crud import prompt as crud_prompt
from app.database import get_db
from app.schemas.prompt import PromptCreate

router = APIRouter(prefix="/import", tags=["import"])
logger = get_logger(__name__)


class ImportItem(BaseModel):
    """Элемент для импорта"""

    tg_message_id: int
    tg_channel_id: int
    text: str
    is_pinned: bool = False


class ImportRequest(BaseModel):
    """Запрос на импорт"""

    items: List[ImportItem]


class ImportResponse(BaseModel):
    """Ответ на импорт"""

    created: int
    skipped: int
    errors: List[str] = []


@router.post("/", response_model=ImportResponse, status_code=status.HTTP_200_OK)
async def import_prompts(
    import_data: ImportRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """
    Импорт промптов из JSON

    Пропускает дубликаты по tg_message_id
    """
    created = 0
    skipped = 0
    errors = []

    for item in import_data.items:
        try:
            # Проверка на существование
            existing = crud_prompt.get_prompt_by_tg_message_id(db, item.tg_message_id)
            if existing:
                skipped += 1
                continue

            # Создание промпта
            prompt_create = PromptCreate(
                tg_message_id=item.tg_message_id,
                tg_channel_id=item.tg_channel_id,
                text=item.text,
                is_pinned=item.is_pinned,
            )

            crud_prompt.create_prompt(db, prompt_create)
            created += 1

        except Exception as e:
            error_msg = f"Ошибка при импорте промпта {item.tg_message_id}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg, extra={"error": str(e), "tg_message_id": item.tg_message_id})

    logger.info(f"Импорт завершен: создано {created}, пропущено {skipped}, ошибок {len(errors)}")

    return ImportResponse(created=created, skipped=skipped, errors=errors)
