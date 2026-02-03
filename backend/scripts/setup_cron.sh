#!/bin/sh
# Скрипт для настройки cron для резервного копирования

# Добавление задачи в crontab (ежедневно в 2:00)
echo "0 2 * * * /usr/local/bin/python /app/scripts/backup_db.py >> /app/backups/backup.log 2>&1" | crontab -

echo "✅ Cron настроен для ежедневного резервного копирования в 2:00"

