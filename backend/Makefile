# Makefile для удобства работы с проектом

.PHONY: init-migration migrate upgrade downgrade init-db

# Инициализация Alembic (выполнить один раз)
init-migration:
	cd backend && alembic init alembic

# Создание новой миграции
migrate:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# Применение миграций
upgrade:
	cd backend && alembic upgrade head

# Откат миграций
downgrade:
	cd backend && alembic downgrade -1

# Инициализация БД (создание таблиц)
init-db:
	cd backend && python scripts/init_db.py

