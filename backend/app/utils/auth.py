import logging
from fastapi import Depends, HTTPException, status, Request
from app.utils import decode_token
from app.config import get_settings

logger = logging.getLogger()
settings = get_settings()
ADMIN_USERNAME = "admin"
COOKIE_NAME = "auth_token"


def get_user_from_token(token: str) -> dict | None:
    payload = decode_token(token, settings.jwt_secret)
    if not payload:
        return None
    return {"username": payload.get("sub"), "user_id": payload.get("user_id")}


async def get_current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Não autenticado"},
        )

    user = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token inválido ou expirado"},
        )

    logger.info(f"[{user['username']}] Authenticated")
    return user


async def get_admin_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Não autenticado"},
        )

    user = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token inválido ou expirado"},
        )

    logger.info(f"[{user['username']}] Admin authentication attempt")
    if user["username"] != ADMIN_USERNAME:
        logger.warning(f"[{user['username']}] Admin access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Apenas administradores podem executar esta ação"},
        )
    return user


def require_auth(request: Request):
    return get_current_user
