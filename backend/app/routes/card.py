from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime
from database import db, CARDS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignCardDto
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger
from app.routes.tournament import get_tournament
from app.routes.game import get_game, check_game_running, add_game_event
from app.routes.team import get_team
from app.routes.player import get_player

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("", status_code=201)
async def assign_card(card: AssignCardDto, current_user=Depends(get_current_user)):
    get_logger().info(
        f"[{current_user['username']}] Assigning {card.card.value} card - player: {card.player}, game: {card.game}, minute: {card.minute}"
    )
    tournament = await get_tournament(card.tournament)
    game = await get_game(card.game)

    tournament_id = ObjectId(card.tournament)
    get_logger().info("Checking if game is running")
    check_game_running(tournament_id, game)

    get_logger().info(f"Validating player '{card.player}' in team '{card.team}'")
    team = await get_team(card.team)
    player = await get_player(card.player)

    get_logger().info("Checking if player is in game calls")
    game_calls = (
        await db.db["game_calls"]
        .find({"_id": {"$in": [game.get("home_call"), game.get("away_call")]}})
        .to_list(2)
    )

    if len(game_calls) != 2:
        raise Error.game_calls_not_delivered()

    player_oid = ObjectId(card.player)
    in_game = False
    for call in game_calls:
        if player_oid in call.get("players", []):
            in_game = True
            break

    if not in_game:
        raise Error.player_not_in_game()

    get_logger().info(
        f"Recording {card.card.value} card for player '{player['name']}' at minute {card.minute}"
    )
    card_dict = {
        "tournament": ObjectId(card.tournament),
        "team_id": ObjectId(card.team),
        "team_name": team["name"],
        "card": card.card.value,
        "game_id": ObjectId(card.game),
        "player_id": ObjectId(card.player),
        "player_name": player["name"],
        "period": game.get("current_period", 0),
        "minute": card.minute,
        "timestamp": datetime.utcnow(),
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
            "player_id": str(ObjectId(card.player)),
            "player_name": player["name"],
            "team_name": team["name"],
            "period": game.get("current_period", 0),
            "minute": card.minute,
            "card": card.card.value,
            "timestamp": card_dict["timestamp"].isoformat(),
        }
    }

    await add_game_event(ObjectId(card.game), event)
    get_logger().info(
        f"[{current_user['username']}] {card.card.value} card for player '{player['name']}' recorded successfully"
    )

    return {"message": "Card assigned successfully"}
