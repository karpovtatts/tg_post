"""
Скрипт для синхронизации сообщений из Telegram канала в БД
Использует Telethon (Client API) - работает БЕЗ бота в канале
"""

import asyncio
import os
import sys
from typing import List, Optional, Tuple

# Добавление пути к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from telethon import TelegramClient
from telethon.hints import Entity
from telethon.tl.types import Message

from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.crud import prompt as crud_prompt
from app.database import SessionLocal
from app.schemas.prompt import PromptCreate, PromptUpdate

# Настройка логирования
setup_logging(level="INFO")
logger = get_logger(__name__)


def extract_text_from_message(message: Message) -> Optional[str]:
    """Извлечь текст из сообщения"""
    if message.message:
        return message.message
    return None


async def extract_image_url(message: Message, channel_id: int) -> Optional[str]:
    """
    Извлечь URL изображения из сообщения через Telegram Bot API
    URL формируется через getFile и прямой доступ к CDN Telegram.
    Это работает, только если бот имеет доступ к файлу (например, файл публичный).
    """
    if not message.photo:
        return None

    # Проверяем наличие BOT_TOKEN
    if not settings.bot_token or settings.bot_token == "your-telegram-bot-token":
        return None

    try:

        # bot_api_url = f"https://api.telegram.org/bot{settings.bot_token}"

        # Получаем информацию о файле через Bot API
        # Note: Это хак, так как мы не знаем file_id для бота (он отличается от Telethon API)
        # Поэтому здесь мы пока просто логируем, что нужен другой подход
        # Настоящее решение требует скачивания файла через Telethon и загрузки на S3/локально

        # В данный момент мы пропускаем генерацию URL, так как нет надежного способа
        # получить file_id для Bot API, имея только message из Telethon,
        # без пересылки сообщения боту.
        return None

    except Exception as e:
        logger.warning(f"Ошибка при извлечении изображения: {e}")
        return None


async def get_channel_entity(client: TelegramClient, channel_identifier: int | str) -> Optional[Entity]:
    """Получить сущность канала"""
    try:
        entity = await client.get_entity(channel_identifier)
        logger.info(f"Найден канал: {entity.title} (ID: {entity.id})")
        return entity
    except Exception as e:
        logger.error(f"Не удалось найти канал {channel_identifier}: {e}")
        return None


async def process_messages(
    db, client: TelegramClient, messages: List[Message], channel_id: int
) -> Tuple[int, int]:
    """Обработка списка сообщений"""
    created_count = 0
    skipped_count = 0

    for message in messages:
        text = extract_text_from_message(message)
        if not text or len(text.strip()) < 1:
            continue

        # Определение закрепленного сообщения
        is_pinned = getattr(message, "pinned", False)

        # Извлечение изображения
        image_url = await extract_image_url(message, channel_id)

        # Проверка на существование
        existing = crud_prompt.get_prompt_by_tg_message_id(db, message.id)
        if existing:
            # Обновляем, если появилось фото
            if not existing.image_url and image_url:
                crud_prompt.update_prompt(db, existing.id, PromptUpdate(image_url=image_url))
                logger.debug(f"Обновлен промпт {message.id}: добавлено изображение")
            skipped_count += 1
            continue

        # Создание промпта
        try:
            prompt_create = PromptCreate(
                tg_message_id=message.id,
                tg_channel_id=channel_id,
                text=text,
                is_pinned=is_pinned,
                image_url=image_url,
            )

            crud_prompt.create_prompt(db, prompt_create)
            created_count += 1
            logger.debug(f"Создан промпт {'с изображением' if image_url else ''}: {message.id}")

        except Exception as e:
            logger.error(f"Ошибка при создании промпта {message.id}: {e}")

    return created_count, skipped_count


async def sync_channel(limit: Optional[int] = None, offset_id: int = 0):
    """Синхронизировать сообщения из канала"""
    # Проверка настроек
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        logger.error("TELEGRAM_API_ID/HASH должны быть установлены в .env")
        return

    if not settings.channel_id and not settings.channel_username:
        logger.error("CHANNEL_ID/USERNAME должны быть установлены в .env")
        return

    # Определение идентификатора канала
    channel_identifier = settings.channel_username
    if settings.channel_id:
        try:
            channel_identifier = int(settings.channel_id)
        except ValueError:
            pass

    # Создание клиента
    client = TelegramClient("channel_sync_session", int(settings.telegram_api_id), settings.telegram_api_hash)
    db = SessionLocal()

    try:
        await client.start(phone=settings.telegram_phone)
        logger.info("Подключение к Telegram установлено")

        entity = await get_channel_entity(client, channel_identifier)
        if not entity:
            return

        logger.info(f"Загрузка сообщений из канала (лимит: {limit or 'все'})...")

        messages = []
        async for message in client.iter_messages(entity, limit=limit, offset_id=offset_id):
            if isinstance(message, Message):
                messages.append(message)

        logger.info(f"Загружено {len(messages)} сообщений")

        created, skipped = await process_messages(db, client, messages, entity.id)
        logger.info(f"Синхронизация завершена: создано {created}, пропущено {skipped}")

    except Exception as e:
        logger.error(f"Ошибка при синхронизации: {e}", extra={"error": str(e)})
    finally:
        await client.disconnect()
        db.close()


async def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Синхронизация сообщений из Telegram канала")
    parser.add_argument("--limit", type=int, help="Максимальное количество сообщений")
    parser.add_argument("--offset-id", type=int, default=0, help="ID сообщения для начала загрузки")

    args = parser.parse_args()
    await sync_channel(limit=args.limit, offset_id=args.offset_id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка по запросу пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", extra={"error": str(e)})
        sys.exit(1)
