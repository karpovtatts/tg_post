"""
Точка входа для запуска Telegram бота
"""
from app.bot.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

