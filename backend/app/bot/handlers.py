"""
Обработчики событий Telegram канала
"""

from typing import Optional

import aiohttp
from aiogram import Router
from aiogram.types import Message

from app.bot.api_client import APIClient
from app.bot.config import CHANNEL_ID
from app.bot.retry import retry_with_backoff
from app.core.logging_config import get_logger

router = Router()
logger = get_logger(__name__)
api_client = APIClient()


def extract_text_from_message(message: Message) -> Optional[str]:
    """
    Извлечь текст из сообщения

    Поддерживает:
    - Обычный текст
    - Текст с форматированием (HTML/Markdown)
    - Текст из подписи к медиа
    """
    if message.text:
        return message.text
    elif message.caption:
        return message.caption
    return None


@router.channel_post()
async def handle_channel_post(message: Message, session: aiohttp.ClientSession):
    """
    Обработчик новых постов в канале

    Правила:
    - Если tg_message_id не существует → создать
    - Иначе → игнорировать (дедупликация)
    """
    # Проверка канала
    if message.chat.id != CHANNEL_ID:
        logger.debug(f"Пост из другого канала: {message.chat.id}, ожидался {CHANNEL_ID}")
        return

    text = extract_text_from_message(message)
    if not text:
        logger.debug(f"Пост {message.message_id} не содержит текста, пропускаем")
        return

    # Проверка минимальной длины
    if len(text.strip()) < 1:
        logger.debug(f"Пост {message.message_id} пустой, пропускаем")
        return

    logger.info(f"Получен новый пост из канала: {message.message_id}")

    # Извлечение изображения (если есть)
    image_url = None
    if message.photo:
        # Получаем самое большое фото
        largest_photo = max(message.photo, key=lambda p: p.file_size if p.file_size else 0)
        file_id = largest_photo.file_id

        # Получаем file_path через Bot API
        from app.bot.config import BOT_TOKEN

        bot_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        get_file_url = f"{bot_api_url}/getFile"
        get_file_data = {"file_id": file_id}

        try:
            # Используем глобальную сессию
            async with session.post(get_file_url, json=get_file_data) as file_response:
                if file_response.status == 200:
                    file_result = await file_response.json()
                    if file_result.get("ok"):
                        file_path = file_result["result"].get("file_path")
                        if file_path:
                            # Формируем прямой URL к изображению
                            image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                            logger.info(f"✅ Получен URL изображения для сообщения {message.message_id}")
        except Exception as e:
            logger.warning(f"Ошибка при получении URL изображения для сообщения {message.message_id}: {e}")

    # Попытка создания с повторами
    result = await retry_with_backoff(
        api_client.create_prompt,
        session=session,
        tg_message_id=message.message_id,
        tg_channel_id=message.chat.id,
        text=text,
        is_pinned=message.chat.pinned_message and message.chat.pinned_message.message_id == message.message_id,
        image_url=image_url,
    )

    if result:
        logger.info(f"Промпт успешно создан: {message.message_id}")
    else:
        logger.warning(f"Не удалось создать промпт: {message.message_id}")


@router.edited_channel_post()
async def handle_edited_channel_post(message: Message, session: aiohttp.ClientSession):
    """
    Обработчик отредактированных постов в канале

    Правила:
    - Обновить text + updated_at
    """
    # Проверка канала
    if message.chat.id != CHANNEL_ID:
        return

    text = extract_text_from_message(message)
    if not text:
        logger.debug(f"Отредактированный пост {message.message_id} не содержит текста")
        return

    logger.info(f"Получен отредактированный пост: {message.message_id}")

    # Извлечение изображения (если есть)
    image_url = None
    if message.photo:
        # Получаем самое большое фото
        largest_photo = max(message.photo, key=lambda p: p.file_size if p.file_size else 0)
        file_id = largest_photo.file_id

        # Получаем file_path через Bot API
        from app.bot.config import BOT_TOKEN

        bot_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        get_file_url = f"{bot_api_url}/getFile"
        get_file_data = {"file_id": file_id}

        try:
            # Используем глобальную сессию
            async with session.post(get_file_url, json=get_file_data) as file_response:
                if file_response.status == 200:
                    file_result = await file_response.json()
                    if file_result.get("ok"):
                        file_path = file_result["result"].get("file_path")
                        if file_path:
                            # Формируем прямой URL к изображению
                            image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                            logger.info(f"✅ Получен URL изображения для сообщения {message.message_id}")
        except Exception as e:
            logger.warning(f"Ошибка при получении URL изображения для сообщения {message.message_id}: {e}")

    # Попытка обновления с повторами
    result = await retry_with_backoff(
        api_client.update_prompt, session=session, tg_message_id=message.message_id, text=text, image_url=image_url
    )

    if result:
        logger.info(f"Промпт успешно обновлен: {message.message_id}")
    else:
        logger.warning(f"Не удалось обновить промпт: {message.message_id}")


async def handle_delete_message(tg_message_id: int, tg_channel_id: int, session: aiohttp.ClientSession = None):
    """
    Обработчик удаления поста

    Вызывается вручную при получении информации об удалении поста
    (через webhook или другой механизм)

    Args:
        tg_message_id: ID удаленного сообщения
        tg_channel_id: ID канала
        session: aiohttp сессия (если есть)
    """
    # Проверка канала
    if tg_channel_id != CHANNEL_ID:
        logger.debug(f"Удаление из другого канала: {tg_channel_id}, ожидался {CHANNEL_ID}")
        return

    logger.info(f"Получено уведомление об удалении поста: {tg_message_id}")

    if session is None:
        # Fallback если сессии нет (хотя должна быть)
        async with aiohttp.ClientSession() as temp_session:
            result = await retry_with_backoff(
                api_client.delete_prompt, session=temp_session, tg_message_id=tg_message_id
            )
            return

    # Попытка удаления с повторами
    result = await retry_with_backoff(api_client.delete_prompt, session=session, tg_message_id=tg_message_id)

    if result:
        logger.info(f"Промпт успешно удален: {tg_message_id}")
    else:
        logger.warning(f"Не удалось удалить промпт: {tg_message_id}")
