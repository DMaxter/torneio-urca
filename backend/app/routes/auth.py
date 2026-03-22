import logging
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status
from database import db, USERS_COLLECTION
from app.routes.user import verify_password
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


class LoginDto(BaseModel):
    username: str
    password: str


class TokenDto(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


@router.post("/login", response_model=TokenDto)
async def login(credentials: LoginDto):
    logger.info(f"Login attempt for user: {credentials.username}")
    user = await db.db[USERS_COLLECTION].find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["password"]):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    token = create_access_token({"sub": user["username"], "user_id": str(user["_id"])})
    logger.info(f"Successful login for user: {credentials.username}")
    return TokenDto(access_token=token)
