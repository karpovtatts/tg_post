"""
Главный файл для запуска Telegram бота
"""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.config import BOT_TOKEN, CHANNEL_ID
from app.bot.handlers import router as channel_router
from app.bot.commands import router as commands_router
from app.core.logging_config import setup_logging, get_logger

# Настройка логирования
setup_logging(level="INFO")
logger = get_logger(__name__)


async def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в переменных окружения")
        sys.exit(1)
    
    if not CHANNEL_ID:
        logger.error("CHANNEL_ID не установлен в переменных окружения")
        sys.exit(1)
    
    logger.info(f"Запуск Telegram бота для канала {CHANNEL_ID}")
    
    # Создание бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(channel_router)  # Обработчики канала
    dp.include_router(commands_router)  # Команды бота
    
    try:
        # Запуск polling
        logger.info("Бот запущен, ожидание сообщений...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Критическая ошибка бота: {e}", extra={"error": str(e)})
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка бота по запросу пользователя")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", extra={"error": str(e)})
        sys.exit(1)

