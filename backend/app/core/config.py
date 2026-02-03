"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    
    # API Security
    api_secret: Optional[str] = None
    bot_secret: Optional[str] = None
    
    # Telegram
    bot_token: Optional[str] = None
    channel_id: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./data/promptvault.db"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

