from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Response, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from database import db, USERS_COLLECTION
from app.routes.user import verify_password
from app.config import get_settings
from app.utils import get_logger, decode_token, ALGORITHM
from app.utils.auth import COOKIE_NAME

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


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
    """
    Generate a JWT access token encoding the provided payload along with an expiration time.

    Args:
        data: The dictionary payload intended for the token.
              Should include 'sub' for the username and 'user_id'.
    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


@router.post("/login", response_model=TokenDto)
@limiter.limit("5/minute")
async def login(credentials: LoginDto, response: Response, request: Request):
    """
    Authenticate a user using their username and password.

    Rate-limited to 5 attempts per minute per IP to prevent brute-force attacks.
    Upon successful authentication, a JWT is generated and set securely as an HTTP-only
    cookie. In a production environment, the cookie will be flagged as secure and same-site.

    Raises:
        HTTPException(401) on invalid credentials.
        HTTPException(429) when rate limit is exceeded.
    """
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
    """
    Terminate the user session by explicitly clearing the configured JWT auth cookie.
    Includes configuration branching to respect secure contexts in production.
    """
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
    """
    Retrieve the current authenticated user context directly from the request cookies.
    Fails gracefully returning None if the token is non-existent, invalid, or expired.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = decode_token(token, settings.jwt_secret)
    if not payload:
        return None
    return CurrentUserDto(
        username=payload.get("sub", ""), user_id=payload.get("user_id", "")
    )
