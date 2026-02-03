# API версии 1
import importlib

from fastapi import APIRouter

from app.api.v1 import prompts, search, tags

api_router = APIRouter()

api_router.include_router(prompts.router)
api_router.include_router(tags.router)
api_router.include_router(search.router)

# Импорт модуля import через importlib (import - зарезервированное слово)
import_module = importlib.import_module("app.api.v1.import")
api_router.include_router(import_module.router)
