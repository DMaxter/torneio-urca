from bson import ObjectId
from fastapi import APIRouter
from datetime import datetime
from database import db, CARDS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignCardDto
from app.error import Error
from app.routes.tournament import get_tournament
from app.routes.game import get_game, check_game_running, add_game_event
from app.routes.team import get_team
from app.routes.user import get_player

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("", status_code=201)
async def assign_card(card: AssignCardDto):
    tournament = await get_tournament(card.tournament)
    game = await get_game(card.game)

    tournament_id = ObjectId(card.tournament)
    check_game_running(tournament_id, game)

    team = await get_team(card.team)
    player = await get_player(card.player)

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

    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"cards": card_dict}}
    )

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

    return {"message": "Card assigned successfully"}
