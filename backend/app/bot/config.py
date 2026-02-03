"""
Конфигурация Telegram бота
"""

from app.core.config import settings

BOT_TOKEN = settings.bot_token
BOT_SECRET = settings.bot_secret
CHANNEL_ID = int(settings.channel_id) if settings.channel_id else None
API_BASE_URL = "http://localhost:8000"  # В production изменить на реальный URL
API_SECRET = settings.api_secret
