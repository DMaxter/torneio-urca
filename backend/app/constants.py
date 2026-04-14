from datetime import datetime, timezone

# Tournament validation constraints
MIN_PLAYERS = 5
MAX_PLAYERS = 14
TOURNAMENT_START_DATE = datetime(2026, 5, 28, tzinfo=timezone.utc)
AGE_FOR_ENROLLMENT = 16  # Cannot enroll if under this age
AGE_REQUIRES_AUTHORIZATION = 18  # Requires authorization if under this age

# File upload constraints
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# File naming prefixes used in team registration
STAFF_FILE_PREFIXES = ["main_coach", "physiotherapist", "first_deputy", "second_deputy"]
PLAYER_FILE_PREFIX = "player"
