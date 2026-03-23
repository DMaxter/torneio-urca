import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils import decode_token
from app.config import get_settings

logger = logging.getLogger()
security = HTTPBearer()
settings = get_settings()
ADMIN_USERNAME = "admin"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_token(token, settings.jwt_secret)
    user = {"username": payload.get("sub"), "user_id": payload.get("user_id")}
    logger.info(f"[{user['username']}] Authenticated")
    return user


async def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_token(token, settings.jwt_secret)
    user = {"username": payload.get("sub"), "user_id": payload.get("user_id")}
    logger.info(f"[{user['username']}] Admin authentication attempt")
    if user["username"] != ADMIN_USERNAME:
        logger.warning(f"[{user['username']}] Admin access denied")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Apenas administradores podem executar esta ação"},
        )
    return user


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return get_current_user
