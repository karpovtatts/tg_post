"""
Скрипт для инициализации базы данных
"""
import sys
import os

# Добавление пути к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models import Prompt, Tag, PromptTag

def init_db():
    """Создание всех таблиц в БД"""
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()

