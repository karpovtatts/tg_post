# Pydantic схемы для валидации данных
from app.schemas.prompt import (
    PromptBase,
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse,
    TagResponse as PromptTagResponse
)
from app.schemas.tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagResponse
)

__all__ = [
    "PromptBase",
    "PromptCreate",
    "PromptUpdate",
    "PromptResponse",
    "PromptListResponse",
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagResponse",
]
