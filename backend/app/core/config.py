"""
Конфигурация приложения
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

# Определяем путь к корню проекта (где находится .env)
# Ищем корень проекта: идем вверх от backend/app/core/config.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""

    # API Security
    api_secret: Optional[str] = None
    bot_secret: Optional[str] = None

    # Telegram
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None
    channel_username: Optional[str] = None

    # Telegram Client API (для чтения без бота)
    telegram_api_id: Optional[str] = None
    telegram_api_hash: Optional[str] = None
    telegram_phone: Optional[str] = None

    # Database
    database_url: str = "sqlite:///./data/promptvault.db"

    # Environment
    environment: str = "development"

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорировать дополнительные поля из .env


settings = Settings()
