"""
API клиент для взаимодействия с backend
"""

from typing import Any, Dict, Optional

import aiohttp

from app.bot.config import API_BASE_URL, API_SECRET
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class APIClient:
    """Клиент для работы с PromptVault API"""

    def __init__(self, base_url: str = API_BASE_URL, api_secret: Optional[str] = API_SECRET):
        self._base_url = base_url.rstrip("/")
        self.api_secret = api_secret
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_secret:
            self.headers["Authorization"] = f"Bearer {self.api_secret}"

    @property
    def base_url(self) -> str:
        """Getter для base_url"""
        return self._base_url

    async def create_prompt(
        self,
        session: aiohttp.ClientSession,
        tg_message_id: int,
        tg_channel_id: int,
        text: str,
        is_pinned: bool = False,
        image_url: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Создать новый промпт

        Returns:
            Dict с данными промпта или None при ошибке
        """
        url = f"{self._base_url}/api/v1/prompts"
        data = {"tg_message_id": tg_message_id, "tg_channel_id": tg_channel_id, "text": text, "is_pinned": is_pinned}
        if image_url:
            data["image_url"] = image_url

        try:
            async with session.post(url, json=data, headers=self.headers) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Промпт создан: {tg_message_id}")
                    return result
                elif response.status == 409:
                    # Конфликт - промпт уже существует
                    logger.debug(f"Промпт {tg_message_id} уже существует, пропускаем")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при создании промпта {tg_message_id}: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Исключение при создании промпта {tg_message_id}: {e}", extra={"error": str(e)})
            return None

    async def update_prompt(
        self, session: aiohttp.ClientSession, tg_message_id: int, text: str, image_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить промпт по tg_message_id

        Returns:
            Dict с обновленными данными или None при ошибке
        """
        url = f"{self._base_url}/api/v1/prompts/by-tg-id/{tg_message_id}"
        data = {"text": text}
        if image_url:
            data["image_url"] = image_url

        try:
            async with session.patch(url, json=data, headers=self.headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Промпт обновлен: {tg_message_id}")
                    return result
                elif response.status == 404:
                    logger.warning(f"Промпт {tg_message_id} не найден для обновления")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при обновлении промпта {tg_message_id}: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Исключение при обновлении промпта {tg_message_id}: {e}", extra={"error": str(e)})
            return None

    async def delete_prompt(self, session: aiohttp.ClientSession, tg_message_id: int) -> bool:
        """
        Мягкое удаление промпта по tg_message_id

        Returns:
            True если успешно, False при ошибке
        """
        url = f"{self._base_url}/api/v1/prompts/by-tg-id/{tg_message_id}"

        try:
            async with session.delete(url, headers=self.headers) as response:
                if response.status == 204:
                    logger.info(f"Промпт удален: {tg_message_id}")
                    return True
                elif response.status == 404:
                    logger.warning(f"Промпт {tg_message_id} не найден для удаления")
                    return False
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при удалении промпта {tg_message_id}: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Исключение при удалении промпта {tg_message_id}: {e}", extra={"error": str(e)})
            return False

    async def get_prompt_by_tg_id(self, session: aiohttp.ClientSession, tg_message_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить промпт по tg_message_id

        Returns:
            Dict с данными промпта или None
        """
        url = f"{self._base_url}/api/v1/prompts/by-tg-id/{tg_message_id}"

        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при получении промпта {tg_message_id}: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Исключение при получении промпта {tg_message_id}: {e}", extra={"error": str(e)})
            return None
