from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from database import db, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignFoulDto
from app.models.models import GameStatus
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger
from app.utils.game_events import (
    get_game_calls_for_team,
    resolve_player_from_call,
    resolve_staff_from_call,
    calculate_event_second,
)
from app.routes.tournament import get_tournament
from app.routes.game import get_game, add_game_event
from app.routes.team import get_team

router = APIRouter(prefix="/fouls", tags=["Fouls"])


@router.post("", status_code=201)
async def assign_foul(foul: AssignFoulDto, current_user=Depends(get_current_user)):
    get_logger().info(
        f"[{current_user['username']}] Assigning foul - player_number: {foul.player_number}, game: {foul.game}, minute: {foul.minute}"
    )
    tournament = await get_tournament(foul.tournament)
    game = await get_game(foul.game)

    if game.get("status") != GameStatus.InProgress:
        raise Error.bad_request("O jogo não está em progresso")

    get_logger().info(f"Validating team '{foul.team}'")
    team = await get_team(foul.team)

    player_name = ""
    player_id = None
    staff_name = ""
    staff_type = None

    get_logger().info("Looking up team call in game calls")
    team_call, _ = await get_game_calls_for_team(game, foul.team)

    if foul.player_number is not None:
        player_id, player_name = await resolve_player_from_call(
            team_call, foul.player_number
        )
    elif foul.staff_id:
        staff_name, staff_type = await resolve_staff_from_call(team_call, foul.staff_id)

    get_logger().info(f"Recording foul at minute {foul.minute}")
    event_second = calculate_event_second(game, foul.second)

    now = datetime.now(timezone.utc)
    foul_dict = {
        "tournament": ObjectId(foul.tournament),
        "team_id": ObjectId(foul.team),
        "team_name": team["name"],
        "game_id": ObjectId(foul.game),
        "player_id": ObjectId(player_id) if player_id else None,
        "player_name": player_name,
        "player_number": foul.player_number,
        "staff_id": ObjectId(foul.staff_id) if foul.staff_id else None,
        "staff_name": staff_name,
        "staff_type": staff_type,
        "period": game.get("current_period", 0),
        "minute": foul.minute,
        "second": event_second,
        "is_direct_free_kick": foul.is_direct_free_kick,
        "timestamp": now,
    }

    result = await db.db["fouls"].insert_one(foul_dict)
    foul_dict["_id"] = result.inserted_id

    get_logger().info("Updating tournament with foul")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"fouls": foul_dict}}
    )

    get_logger().info("Adding foul event to game")
    event = {
        "Foul": {
            "player_id": player_id,
            "player_name": player_name,
            "player_number": foul.player_number,
            "staff_id": foul.staff_id,
            "staff_name": staff_name,
            "staff_type": staff_type,
            "team_name": team["name"],
            "period": game.get("current_period", 0),
            "minute": foul.minute,
            "second": event_second,
            "card": None,
            "is_direct_free_kick": foul.is_direct_free_kick,
            "timestamp": now.isoformat(),
        }
    }

    await add_game_event(ObjectId(foul.game), event)
    get_logger().info(f"[{current_user['username']}] Foul recorded successfully")

    return {"message": "Foul assigned successfully"}
