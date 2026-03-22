from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils import decode_token
from app.config import get_settings

security = HTTPBearer()
settings = get_settings()
ADMIN_USERNAME = "admin"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_token(token, settings.jwt_secret)
    return {"username": payload.get("sub"), "user_id": payload.get("user_id")}


async def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_token(token, settings.jwt_secret)
    user = {"username": payload.get("sub"), "user_id": payload.get("user_id")}
    if user["username"] != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem executar esta ação",
        )
    return user


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return get_current_user
