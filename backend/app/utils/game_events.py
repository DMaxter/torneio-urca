"""
Shared helpers for game event routes (goals, cards, fouls).

Avoids duplicating player/staff lookup and elapsed-time logic
across goal.py, card.py, and foul.py.
"""

from typing import Optional, Tuple
from bson import ObjectId
from datetime import datetime, timezone
from database import db
from app.error import Error


async def get_game_calls_for_team(game: dict, team_id: str) -> Tuple[dict, list]:
    """
    Fetch both game calls and return the one belonging to `team_id`.

    Returns:
        (team_call, all_calls) — the specific team's call and the full list.
    Raises:
        HTTPException(403) if calls haven't been delivered yet.
        HTTPException(400) if no call is found for `team_id`.
    """
    game_calls = (
        await db.db["game_calls"]
        .find({"_id": {"$in": [game.get("home_call"), game.get("away_call")]}})
        .to_list(2)
    )

    if len(game_calls) != 2:
        raise Error.game_calls_not_delivered()

    team_call = next(
        (call for call in game_calls if str(call.get("team")) == str(team_id)),
        None,
    )

    if not team_call:
        raise Error.bad_request("Chamada de jogo não encontrada para esta equipa")

    return team_call, game_calls


async def resolve_player_from_call(
    team_call: dict, player_number: int
) -> Tuple[Optional[str], str]:
    """
    Look up a player by shirt number within a game call.

    Returns:
        (player_id, player_name)
    Raises:
        HTTPException(400) if the player number is not in the call.
    """
    player_id = None
    for p in team_call.get("players", []):
        if p.get("number") == player_number:
            player_id = p.get("player")
            break

    if not player_id:
        raise Error.bad_request(
            f"Jogador com número {player_number} não encontrado na chamada"
        )

    player = await db.db["players"].find_one({"_id": player_id})
    player_name = player["name"] if player else ""
    return str(player_id), player_name


async def resolve_staff_from_call(
    team_call: dict, staff_id: str
) -> Tuple[str, Optional[str]]:
    """
    Look up a staff member by ID within a game call.

    Returns:
        (staff_name, staff_type)
    Raises:
        HTTPException(400) if the staff member is not in the call.
    """
    staff_in_call = any(
        str(s_id) == str(staff_id) for s_id in team_call.get("staff", [])
    )
    if not staff_in_call:
        raise Error.bad_request(
            "Membro do staff não encontrado na chamada deste jogo"
        )

    staff = await db.db["staff"].find_one({"_id": ObjectId(staff_id)})
    if staff:
        return staff["name"], staff.get("staff_type")
    return "", None


def calculate_event_second(game: dict, provided_second: Optional[int]) -> int:
    """
    Derive the in-period second at which an event occurred.

    Uses `provided_second` if explicitly supplied; otherwise calculates
    live elapsed time from the running timer to get the current second
    within the minute.
    """
    if provided_second is not None:
        return provided_second

    current_elapsed = game.get("period_elapsed_seconds", 0)
    if game.get("timer_active") and game.get("timer_started_at"):
        now_utc = datetime.now(timezone.utc)
        timer_started = game["timer_started_at"]
        if timer_started.tzinfo is None:
            timer_started = timer_started.replace(tzinfo=timezone.utc)
        active_elapsed = int((now_utc - timer_started).total_seconds())
        current_elapsed += active_elapsed

    return current_elapsed % 60
