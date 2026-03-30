from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Response, Request
from database import db, USERS_COLLECTION
from app.routes.user import verify_password
from app.config import get_settings
from app.utils import get_logger, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
COOKIE_NAME = "auth_token"


class LoginDto(BaseModel):
    username: str
    password: str


class TokenDto(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserDto(BaseModel):
    username: str
    user_id: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


@router.post("/login", response_model=TokenDto)
async def login(credentials: LoginDto, response: Response):
    get_logger().info(f"Login attempt for user '{credentials.username}'")
    user = await db.db[USERS_COLLECTION].find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["password"]):
        get_logger().warning(
            f"Failed login attempt for user '{credentials.username}' - invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    token = create_access_token({"sub": user["username"], "user_id": str(user["_id"])})
    get_logger().info(f"User '{credentials.username}' logged in successfully")

    cookie_params = {
        "key": COOKIE_NAME,
        "value": token,
        "httponly": True,
        "max_age": 60 * 60 * 24,
    }
    if settings.production:
        cookie_params["secure"] = True
        cookie_params["samesite"] = "none"
    else:
        cookie_params["samesite"] = "lax"

    response.set_cookie(**cookie_params)
    return TokenDto(access_token=token)


@router.post("/logout")
async def logout(response: Response):
    cookie_params = {"key": COOKIE_NAME}
    if settings.production:
        cookie_params["secure"] = True
        cookie_params["samesite"] = "none"
    else:
        cookie_params["samesite"] = "lax"
    response.delete_cookie(**cookie_params)
    return {"message": "Logged out"}


@router.get("/me", response_model=CurrentUserDto | None)
async def get_current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = decode_token(token, settings.jwt_secret)
    if not payload:
        return None
    return CurrentUserDto(
        username=payload.get("sub", ""), user_id=payload.get("user_id", "")
    )
