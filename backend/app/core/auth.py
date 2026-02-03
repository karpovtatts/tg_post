"""
Аутентификация через Bearer token
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

security = HTTPBearer()


def verify_api_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """
    Проверка API токена из заголовка Authorization

    Args:
        credentials: Bearer токен из заголовка

    Returns:
        bool: True если токен валиден

    Raises:
        HTTPException: Если токен неверный или отсутствует
    """
    if not settings.api_secret:
        # В development режиме без токена можно пропустить проверку
        if settings.environment == "development":
            return True
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_SECRET не настроен",
        )

    token = credentials.credentials

    if token != settings.api_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный API токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def verify_bot_secret(secret: str) -> bool:
    """
    Проверка секрета для Telegram бота

    Args:
        secret: Секрет из запроса

    Returns:
        bool: True если секрет валиден
    """
    return secret == settings.bot_secret


# Dependency для защищенных эндпоинтов
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Dependency для получения текущего пользователя (проверка токена)
    """
    verify_api_token(credentials)
    return {"authenticated": True}
