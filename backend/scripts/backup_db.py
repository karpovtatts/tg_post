#!/usr/bin/env python3
"""
Скрипт для резервного копирования базы данных SQLite
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Добавление пути к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


BACKUP_DIR = Path("/app/backups")
DB_PATH = Path("/app/data/promptvault.db")
RETENTION_DAYS = 7


def create_backup():
    """Создать резервную копию БД"""
    if not DB_PATH.exists():
        print(f"❌ База данных не найдена: {DB_PATH}")
        return False

    # Создание директории для бэкапов
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Имя файла бэкапа с датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"promptvault_{timestamp}.db"
    backup_path = BACKUP_DIR / backup_filename

    try:
        # Копирование БД
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Резервная копия создана: {backup_path}")

        # Очистка старых бэкапов
        cleanup_old_backups()

        return True
    except Exception as e:
        print(f"❌ Ошибка при создании резервной копии: {e}")
        return False


def cleanup_old_backups():
    """Удалить резервные копии старше RETENTION_DAYS дней"""
    if not BACKUP_DIR.exists():
        return

    now = datetime.now()
    deleted_count = 0

    for backup_file in BACKUP_DIR.glob("promptvault_*.db"):
        try:
            # Получение времени модификации файла
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            age_days = (now - mtime).days

            if age_days > RETENTION_DAYS:
                backup_file.unlink()
                deleted_count += 1
                print(f"🗑️  Удален старый бэкап: {backup_file.name} (возраст: {age_days} дней)")
        except Exception as e:
            print(f"⚠️  Ошибка при удалении {backup_file.name}: {e}")

    if deleted_count > 0:
        print(f"✅ Удалено старых бэкапов: {deleted_count}")


if __name__ == "__main__":
    success = create_backup()
    sys.exit(0 if success else 1)
