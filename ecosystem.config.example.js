/**
 * PM2 конфигурация для PromptVault (без Docker)
 * 
 * Скопируйте этот файл в ecosystem.config.js и адаптируйте под ваш сервер
 * 
 * Использование:
 * pm2 start ecosystem.config.js --update-env
 * pm2 save
 */
module.exports = {
  apps: [
    {
      name: 'promptvault-backend',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      cwd: '/home/your-user/projects/promptvault/backend',  // Измените на ваш путь
      interpreter: 'python3',
      env: {
        ENVIRONMENT: 'production',
      },
      env_file: '/home/your-user/projects/promptvault/.env',  // Измените на ваш путь
      error_file: '/home/your-user/projects/promptvault/logs/backend-error.log',
      out_file: '/home/your-user/projects/promptvault/logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      instances: 1,
      // Healthcheck через PM2
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
    },
    {
      name: 'promptvault-bot',
      script: 'bot.py',
      cwd: '/home/your-user/projects/promptvault/backend',  // Измените на ваш путь
      interpreter: 'python3',
      env: {
        ENVIRONMENT: 'production',
      },
      env_file: '/home/your-user/projects/promptvault/.env',  // Измените на ваш путь
      error_file: '/home/your-user/projects/promptvault/logs/bot-error.log',
      out_file: '/home/your-user/projects/promptvault/logs/bot-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      instances: 1,
      // Healthcheck через PM2
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
    },
  ],
};

