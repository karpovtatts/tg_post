"""
Скрипт для инициализации базы данных
"""

import os
import sys

# Добавление пути к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, engine


def init_db():
    """Создание всех таблиц в БД"""
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")


if __name__ == "__main__":
    init_db()
