# Скрипт быстрого запуска для Windows
# Запускает: Backend, Frontend и Telegram Bot в отдельных окнах

Write-Host "🚀 Запуск PromptVault Development Environment..." -ForegroundColor Green

# 1. Проверка Python Virtual Environment
$venvPath = Join-Path $PSScriptRoot "backend\venv"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "⚠️ Виртуальное окружение не найдено. Создаем..." -ForegroundColor Yellow
    Set-Location "backend"
    python -m venv venv
    
    # Активация и установка зависимостей
    Write-Host "📦 Установка Python зависимостей..." -ForegroundColor Cyan
    & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt
    Set-Location ..
}

# 2. Проверка Node Modules
$nodePath = Join-Path $PSScriptRoot "frontend\node_modules"
if (-not (Test-Path $nodePath)) {
    Write-Host "⚠️ node_modules не найдены. Устанавливаем..." -ForegroundColor Yellow
    Set-Location "frontend"
    npm install
    Set-Location ..
}

# 3. Запуск Backend
Write-Host "🔥 Запуск Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\activate; uvicorn app.main:app --reload --port 8000"

# 4. Запуск Frontend
Write-Host "🎨 Запуск Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# 5. Запуск Telegram Bot
Write-Host "🤖 Запуск Telegram Bot..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\activate; python bot.py"

Write-Host "✅ Все сервисы запущены в новых окнах!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend: http://localhost:8000"
