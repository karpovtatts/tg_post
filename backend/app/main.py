"""
Главный файл FastAPI приложения PromptVault
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.database import Base, engine

# Настройка логирования
setup_logging(level="INFO" if settings.environment == "production" else "DEBUG")
logger = get_logger(__name__)

app = FastAPI(title="PromptVault API", description="API для управления промптами из Telegram канала", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    logger.info("Запуск PromptVault API")
    # Создание таблиц (в production использовать миграции)
    if settings.environment == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы БД созданы (development режим)")

        # Инициализация FTS5
        try:
            from app.database import SessionLocal
            from app.search.fts5 import init_fts5_table

            db = SessionLocal()
            init_fts5_table(db)
            db.close()
            logger.info("FTS5 таблица инициализирована")
        except Exception as e:
            logger.warning(f"Не удалось инициализировать FTS5: {e}", extra={"error": str(e)})


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке приложения"""
    logger.info("Остановка PromptVault API")


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы API"""
    return {"message": "PromptVault API работает", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Эндпоинт для проверки здоровья сервиса"""
    return {"status": "ok"}
