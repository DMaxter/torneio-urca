import jwt
import logging
from bson import ObjectId
from contextvars import ContextVar
from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.constants import MIN_AGE

ALGORITHM = "HS256"
REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="no-request-id")


def sanitize_for_serialization(obj):
    """Recursively convert ObjectId to string for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_for_serialization(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_serialization(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj


class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = REQUEST_ID.get()
        return True


_base_logger = logging.getLogger()
_base_logger.addFilter(RequestIdFilter())


def get_logger() -> logging.Logger:
    """Get a logger with request ID context."""
    return _base_logger


def calculate_age(birth_date: datetime) -> int:
    """Calculate age in years from birth date."""
    today = datetime.now(timezone.utc)
    if birth_date.tzinfo is None:
        birth_date = birth_date.replace(tzinfo=timezone.utc)
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def is_under_age(birth_date: datetime, min_age: int = MIN_AGE) -> bool:
    """Check if a person is under the minimum age threshold."""
    return calculate_age(birth_date) < min_age


def decode_token(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "Token expirado"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "Token inválido"}
        )
