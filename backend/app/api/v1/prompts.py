"""
API эндпоинты для работы с промптами
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.logging_config import get_logger
from app.crud import prompt as crud_prompt
from app.database import get_db
from app.schemas.prompt import PromptCreate, PromptListResponse, PromptResponse, PromptUpdate

router = APIRouter(prefix="/prompts", tags=["prompts"])
logger = get_logger(__name__)


@router.get("/", response_model=PromptListResponse)
async def get_prompts(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(50, ge=1, le=100, description="Количество элементов на странице"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    tags: Optional[List[int]] = Query(None, description="Фильтр по ID тегов"),
    pinned: Optional[bool] = Query(None, description="Только закрепленные"),
    db: Session = Depends(get_db),
):
    """Получить список промптов с фильтрацией и пагинацией"""
    try:
        skip = (page - 1) * limit
        prompts, total = crud_prompt.get_prompts(
            db=db, skip=skip, limit=limit, search=search, tag_ids=tags, pinned_only=pinned
        )

        return PromptListResponse(
            items=[PromptResponse.model_validate(p) for p in prompts], total=total, page=page, limit=limit
        )
    except Exception as e:
        logger.error(f"Ошибка при получении списка промптов: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при получении списка промптов"
        )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Получить промпт по ID"""
    prompt = crud_prompt.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    return PromptResponse.model_validate(prompt)


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt: PromptCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Создать новый промпт (требует аутентификации)"""
    try:
        # Проверка на дубликат по tg_message_id
        existing = crud_prompt.get_prompt_by_tg_message_id(db, prompt.tg_message_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Промпт с таким tg_message_id уже существует"
            )

        db_prompt = crud_prompt.create_prompt(db, prompt)
        logger.info(f"Создан промпт: {db_prompt.id}")
        return PromptResponse.model_validate(db_prompt)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании промпта: {e}", extra={"error": str(e)})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при создании промпта")


@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Обновить промпт (требует аутентификации)"""
    db_prompt = crud_prompt.update_prompt(db, prompt_id, prompt_update)
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    logger.info(f"Обновлен промпт: {prompt_id}")
    return PromptResponse.model_validate(db_prompt)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Удалить промпт (мягкое удаление, требует аутентификации)"""
    success = crud_prompt.delete_prompt(db, prompt_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    logger.info(f"Удален промпт: {prompt_id}")


@router.patch("/{prompt_id}/pin", response_model=PromptResponse)
async def pin_prompt(
    prompt_id: int,
    pin: bool = Query(..., description="Закрепить (true) или открепить (false)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Закрепить/открепить промпт (требует аутентификации)"""
    db_prompt = crud_prompt.pin_prompt(db, prompt_id, pin)
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    logger.info(f"Промпт {prompt_id} {'закреплен' if pin else 'откреплен'}")
    return PromptResponse.model_validate(db_prompt)


@router.post("/{prompt_id}/tags/{tag_id}", response_model=PromptResponse)
async def add_tag_to_prompt(
    prompt_id: int, tag_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Добавить тег к промпту (требует аутентификации)"""
    db_prompt = crud_prompt.add_tag_to_prompt(db, prompt_id, tag_id)
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт или тег не найден")

    logger.info(f"Добавлен тег {tag_id} к промпту {prompt_id}")
    return PromptResponse.model_validate(db_prompt)


@router.delete("/{prompt_id}/tags/{tag_id}", response_model=PromptResponse)
async def remove_tag_from_prompt(
    prompt_id: int, tag_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Удалить тег из промпта (требует аутентификации)"""
    db_prompt = crud_prompt.remove_tag_from_prompt(db, prompt_id, tag_id)
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт или тег не найден")

    logger.info(f"Удален тег {tag_id} из промпта {prompt_id}")
    return PromptResponse.model_validate(db_prompt)


@router.get("/by-tg-id/{tg_message_id}", response_model=PromptResponse)
async def get_prompt_by_tg_id(tg_message_id: int, db: Session = Depends(get_db)):
    """Получить промпт по Telegram message ID"""
    prompt = crud_prompt.get_prompt_by_tg_message_id(db, tg_message_id)
    if not prompt or prompt.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    return PromptResponse.model_validate(prompt)


@router.patch("/by-tg-id/{tg_message_id}", response_model=PromptResponse)
async def update_prompt_by_tg_id(
    tg_message_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Обновить промпт по Telegram message ID (требует аутентификации)"""
    prompt = crud_prompt.get_prompt_by_tg_message_id(db, tg_message_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    db_prompt = crud_prompt.update_prompt(db, prompt.id, prompt_update)
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    logger.info(f"Обновлен промпт по tg_message_id: {tg_message_id}")
    return PromptResponse.model_validate(db_prompt)


@router.delete("/by-tg-id/{tg_message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt_by_tg_id(
    tg_message_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Удалить промпт по Telegram message ID (мягкое удаление, требует аутентификации)"""
    prompt = crud_prompt.get_prompt_by_tg_message_id(db, tg_message_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    success = crud_prompt.delete_prompt(db, prompt.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не найден")

    logger.info(f"Удален промпт по tg_message_id: {tg_message_id}")
