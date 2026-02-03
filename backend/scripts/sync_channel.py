"""
Скрипт для синхронизации сообщений из Telegram канала в БД
Использует Telethon (Client API) - работает БЕЗ бота в канале
"""

import asyncio
import os
import sys
from typing import Optional

# Добавление пути к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from telethon import TelegramClient
from telethon.tl.types import Message

from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.crud import prompt as crud_prompt
from app.database import SessionLocal
from app.schemas.prompt import PromptCreate

# Для работы с Bot API
try:
    from aiogram import Bot
    from aiogram.types import Message as BotMessage

    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False

# Настройка логирования
setup_logging(level="INFO")
logger = get_logger(__name__)


def extract_text_from_message(message: Message) -> Optional[str]:
    """Извлечь текст из сообщения"""
    if message.message:
        return message.message
    return None


async def extract_image_url(client: TelegramClient, message: Message, channel_id: int) -> Optional[str]:
    """
    Извлечь URL изображения из сообщения через Telegram Bot API

    Использует Bot API для получения file_path и формирования прямого URL к изображению.
    Для работы нужен BOT_TOKEN в .env.

    Алгоритм:
    1. Пробуем получить file_id через forwardMessage (если бот в канале)
    2. Используем getFile для получения file_path
    3. Формируем URL: https://api.telegram.org/file/bot{token}/{file_path}

    Если бот не в канале, используем альтернативный способ через прямую ссылку на пост.

    Returns:
        URL изображения через Telegram CDN или None
    """
    try:
        if message.photo:
            logger.info(f"Найдено фото в сообщении {message.id}")

            # Проверяем наличие BOT_TOKEN
            if not settings.bot_token or settings.bot_token == "your-telegram-bot-token":
                logger.debug(f"BOT_TOKEN не установлен, пропускаем изображение для сообщения {message.id}")
                return None

            try:

                import aiohttp

                bot_api_url = f"https://api.telegram.org/bot{settings.bot_token}"

                # Формируем channel_id для Bot API (формат -100...)
                bot_channel_id = channel_id
                if bot_channel_id > 0:
                    bot_channel_id = -1000000000000 - bot_channel_id

                # Пробуем получить file_id через forwardMessage
                # Для этого пересылаем сообщение боту самому себе
                async with aiohttp.ClientSession() as session:
                    # Получаем информацию о боте
                    get_me_url = f"{bot_api_url}/getMe"
                    async with session.get(get_me_url) as response:
                        if response.status != 200:
                            logger.warning(f"Не удалось получить информацию о боте: {response.status}")
                            return None

                        bot_info = await response.json()
                        if not bot_info.get("ok"):
                            logger.warning("Бот не авторизован")
                            return None

                        bot_user_id = bot_info["result"]["id"]

                    # Проблема: боты не могут отправлять сообщения другим ботам (ошибка: "Forbidden: bots can't send messages to bots")
                    # Решение: используем информацию о файле из Telethon для скачивания и сохранения локально
                    # Или используем copyMessage в приватный чат с пользователем (нужен chat_id)

                    # Временное решение: возвращаем None
                    # Для полной реализации нужно:
                    # 1. Скачивать изображения через Telethon и сохранять локально (требует настройки сервера)
                    # 2. Или использовать copyMessage в приватный чат с пользователем (нужен chat_id пользователя)
                    # 3. Или получать сообщения через aiogram в реальном времени (только новые сообщения)

                    logger.debug(f"Фото найдено в сообщении {message.id}, но URL не сформирован")
                    logger.info(
                        "Для получения изображений из старых сообщений нужен другой подход (скачивание через Telethon или copyMessage)"
                    )

                    return None

                    # Альтернативный способ: формируем прямую ссылку на пост
                    # Это не даст прямое изображение, но позволит открыть пост
                    channel_id_str = str(abs(channel_id))
                    if channel_id_str.startswith("100"):
                        channel_id_str = channel_id_str[3:]

                    post_url = f"https://t.me/c/{channel_id_str}/{message.id}"
                    logger.debug(f"Сформирована ссылка на пост: {post_url}")
                    # Возвращаем None, так как прямая ссылка не работает в <img>
                    return None

            except Exception as e:
                logger.warning(f"Ошибка при получении URL для сообщения {message.id}: {e}")
        else:
            logger.debug(f"В сообщении {message.id} нет фото")

    except Exception as e:
        logger.warning(f"Ошибка при извлечении изображения из сообщения {message.id}: {e}")

    return None


async def sync_channel(limit: Optional[int] = None, offset_id: int = 0):
    """
    Синхронизировать сообщения из канала

    Args:
        limit: Максимальное количество сообщений для загрузки (None = все)
        offset_id: ID сообщения, с которого начинать (для пагинации)
    """
    # Проверка настроек
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        logger.error("TELEGRAM_API_ID и TELEGRAM_API_HASH должны быть установлены в .env")
        logger.info("Получите их на https://my.telegram.org/apps")
        return

    if not settings.channel_id and not settings.channel_username:
        logger.error("CHANNEL_ID или CHANNEL_USERNAME должны быть установлены в .env")
        return

    # Определение канала (приоритет у ID, если указан)
    if settings.channel_id:
        # Преобразуем ID в int для Telethon
        try:
            channel_identifier = int(settings.channel_id)
        except ValueError:
            logger.error(f"Неверный формат CHANNEL_ID: {settings.channel_id}")
            return
    else:
        channel_identifier = settings.channel_username

    # Создание клиента
    client = TelegramClient("channel_sync_session", int(settings.telegram_api_id), settings.telegram_api_hash)

    db = SessionLocal()
    created_count = 0
    skipped_count = 0

    try:
        # Подключение
        await client.start(phone=settings.telegram_phone)
        logger.info("Подключение к Telegram установлено")

        # Получение канала
        try:
            entity = await client.get_entity(channel_identifier)
            logger.info(f"Найден канал: {entity.title} (ID: {entity.id})")
        except Exception as e:
            logger.error(f"Не удалось найти канал {channel_identifier}: {e}")
            return

        # Получение сообщений
        logger.info(f"Загрузка сообщений из канала (лимит: {limit or 'все'})...")

        messages = []
        async for message in client.iter_messages(entity, limit=limit, offset_id=offset_id):
            if isinstance(message, Message):
                messages.append(message)

        logger.info(f"Загружено {len(messages)} сообщений")

        # Обработка сообщений
        for message in messages:
            text = extract_text_from_message(message)
            if not text or len(text.strip()) < 1:
                continue

            # Определение закрепленного сообщения
            is_pinned = message.pinned if hasattr(message, "pinned") else False

            # Извлечение изображения
            image_url = await extract_image_url(client, message, entity.id)

            # Проверка на существование
            existing = crud_prompt.get_prompt_by_tg_message_id(db, message.id)
            if existing:
                # Обновляем существующий промпт, если нет изображения
                if not existing.image_url and image_url:
                    from app.schemas.prompt import PromptUpdate

                    prompt_update = PromptUpdate(image_url=image_url)
                    crud_prompt.update_prompt(db, existing.id, prompt_update)
                    logger.debug(f"Обновлен промпт {message.id}: добавлено изображение")
                skipped_count += 1
                continue

            # Создание промпта
            try:
                prompt_create = PromptCreate(
                    tg_message_id=message.id,
                    tg_channel_id=entity.id,
                    text=text,
                    is_pinned=is_pinned,
                    image_url=image_url,
                )

                crud_prompt.create_prompt(db, prompt_create)
                created_count += 1
                if image_url:
                    logger.debug(f"Создан промпт с изображением: {message.id}")
                else:
                    logger.debug(f"Создан промпт: {message.id}")

            except Exception as e:
                logger.error(f"Ошибка при создании промпта {message.id}: {e}")

        logger.info(f"Синхронизация завершена: создано {created_count}, пропущено {skipped_count}")

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
