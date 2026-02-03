# PromptVault

Персональное веб-приложение с интеграцией Telegram-бота для сбора, хранения, организации, поиска и копирования промптов для AI.

## Технологический стек

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, SQLite
- **Frontend**: React 18+, TypeScript, Vite, Tailwind CSS
- **Telegram**: aiogram 3.x
- **Инфраструктура**: PM2, Nginx

## Быстрый старт

### Локальная разработка

```bash
# 1. Копирование переменных окружения
cp env.example .env

# 2. Редактирование .env файла
# Заполните BOT_TOKEN, BOT_SECRET, API_SECRET, CHANNEL_ID

# 3. Запуск Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. Запуск Frontend (в другом терминале)
cd frontend
npm install
npm run dev

# 5. Запуск Telegram Bot (в третьем терминале)
cd backend
python bot.py
```

**Доступ к приложению:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Развертывание на сервере

📖 **Инструкция по развертыванию:** 
- Для настройки PM2 используйте [ecosystem.config.example.js](ecosystem.config.example.js) как шаблон

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Telegram Bot

```bash
cd backend
python bot.py
```

**Команды бота:**
- `/start` - приветствие и справка
- `/help` - подробная справка
- `/get <запрос>` - поиск промпта
- `/recent` - последние промпты
- `/pinned` - закрепленные промпты

## Структура проекта

```
.
├── backend/                    # FastAPI приложение
├── frontend/                   # React приложение
├── nginx/                      # Конфигурация Nginx
├── scripts/                    # Скрипты для управления
├── ecosystem.config.example.js # Пример PM2 конфигурации (создайте ecosystem.config.js на основе этого)
└── env.example                 # Шаблон переменных окружения
```

## Развертывание

Проект развертывается через **PM2** (без Docker):
- Используйте `ecosystem.config.example.js` как шаблон для создания `ecosystem.config.js`
## Лицензия

Приватный проект для личного использования.

