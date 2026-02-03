"""
Настройка логирования в формате JSON
"""

import json
import logging
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Форматтер для вывода логов в формате JSON"""

    def format(self, record: logging.LogRecord) -> str:
        """Форматирование записи лога в JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Добавление исключения, если есть
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Добавление дополнительных полей
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """
    Настройка системы логирования

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Создание логгера
    logger = logging.getLogger("promptvault")
    logger.setLevel(getattr(logging, level.upper()))

    # Удаление существующих обработчиков
    logger.handlers = []

    # Создание обработчика для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Установка JSON форматера
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)

    # Добавление обработчика к логгеру
    logger.addHandler(console_handler)

    # Настройка логирования для uvicorn
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    uvicorn_handler = logging.StreamHandler(sys.stdout)
    uvicorn_handler.setFormatter(formatter)
    uvicorn_logger.addHandler(uvicorn_handler)

    # Настройка логирования для SQLAlchemy (только ошибки)
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)


def get_logger(name: str = "promptvault") -> logging.Logger:
    """
    Получить логгер с указанным именем

    Args:
        name: Имя логгера

    Returns:
        logging.Logger: Настроенный логгер
    """
    return logging.getLogger(name)
