from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from database import db, CARDS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignCardDto
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

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("", status_code=201)
async def assign_card(card: AssignCardDto, current_user=Depends(get_current_user)):
    get_logger().info(
        f"[{current_user['username']}] Assigning {card.card.value} card - player_number: {card.player_number}, game: {card.game}, minute: {card.minute}"
    )
    tournament = await get_tournament(card.tournament)
    game = await get_game(card.game)

    if game.get("status") != GameStatus.InProgress:
        raise Error.bad_request("O jogo não está em progresso")

    get_logger().info(f"Validating team '{card.team}'")
    team = await get_team(card.team)

    player_name = ""
    player_id = None
    staff_name = ""
    staff_type = None

    get_logger().info("Looking up team call in game calls")
    team_call, _ = await get_game_calls_for_team(game, card.team)

    if card.player_number is not None:
        player_id, player_name = await resolve_player_from_call(
            team_call, card.player_number
        )
    elif card.staff_id:
        staff_name, staff_type = await resolve_staff_from_call(team_call, card.staff_id)

    get_logger().info(f"Recording {card.card.value} card at minute {card.minute}")
    event_second = calculate_event_second(game, card.second)

    now = datetime.now(timezone.utc)
    card_dict = {
        "tournament": ObjectId(card.tournament),
        "team_id": ObjectId(card.team),
        "team_name": team["name"],
        "card": card.card.value,
        "game_id": ObjectId(card.game),
        "player_id": ObjectId(player_id) if player_id else None,
        "player_name": player_name,
        "player_number": card.player_number,
        "staff_id": ObjectId(card.staff_id) if card.staff_id else None,
        "staff_name": staff_name,
        "staff_type": staff_type,
        "period": game.get("current_period", 0),
        "minute": card.minute,
        "second": event_second,
        "timestamp": now,
    }

    result = await db.db[CARDS_COLLECTION].insert_one(card_dict)
    card_dict["_id"] = result.inserted_id

    get_logger().info("Updating tournament with card")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"cards": card_dict}}
    )

    get_logger().info("Adding card event to game")
    event = {
        "Foul": {
            "player_id": player_id,
            "player_name": player_name,
            "player_number": card.player_number,
            "staff_id": card.staff_id,
            "staff_name": staff_name,
            "staff_type": staff_type,
            "team_name": team["name"],
            "period": game.get("current_period", 0),
            "minute": card.minute,
            "second": event_second,
            "card": card.card.value,
            "is_direct_free_kick": card.is_direct_free_kick,
            "timestamp": now.isoformat(),
        }
    }

    await add_game_event(ObjectId(card.game), event)
    get_logger().info(
        f"[{current_user['username']}] {card.card.value} card recorded successfully"
    )

    return {"message": "Card assigned successfully"}
