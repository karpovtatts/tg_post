"""
Логика повторов при ошибках
"""

import asyncio
from typing import Any, Callable, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Настройки повторов
MAX_RETRIES = 3
INITIAL_DELAY = 1  # секунды
MAX_DELAY = 10  # секунды
BACKOFF_MULTIPLIER = 2


async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = MAX_RETRIES,
    initial_delay: float = INITIAL_DELAY,
    max_delay: float = MAX_DELAY,
    backoff_multiplier: float = BACKOFF_MULTIPLIER,
    **kwargs,
) -> Optional[Any]:
    """
    Выполнить функцию с повторами и экспоненциальной задержкой

    Args:
        func: Асинхронная функция для выполнения
        *args: Позиционные аргументы функции
        max_retries: Максимальное количество попыток
        initial_delay: Начальная задержка в секундах
        max_delay: Максимальная задержка в секундах
        backoff_multiplier: Множитель для экспоненциальной задержки
        **kwargs: Именованные аргументы функции

    Returns:
        Результат функции или None при исчерпании попыток
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            result = await func(*args, **kwargs)
            if result is not None:
                return result

            # Если результат None, но это не ошибка (например, 409 конфликт)
            # то не повторяем
            if attempt == 0:
                return None

        except Exception as e:
            if attempt == max_retries - 1:
                # Последняя попытка - логируем ошибку
                logger.error(
                    f"Исчерпаны попытки для функции {func.__name__}: {e}",
                    extra={"error": str(e), "function": func.__name__, "attempts": max_retries},
                )
                return None

            logger.warning(
                f"Попытка {attempt + 1}/{max_retries} не удалась для {func.__name__}: {e}",
                extra={"error": str(e), "function": func.__name__, "attempt": attempt + 1},
            )

        # Ожидание перед следующей попыткой
        if attempt < max_retries - 1:
            await asyncio.sleep(delay)
            delay = min(delay * backoff_multiplier, max_delay)

    return None
