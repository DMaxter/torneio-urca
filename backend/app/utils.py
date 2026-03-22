from datetime import datetime, timezone

from app.constants import MIN_AGE


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
