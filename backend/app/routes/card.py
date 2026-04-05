from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime
from database import db, CARDS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignCardDto
from app.models.models import GameStatus, StaffType
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger
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

    if card.player_number is not None:
        get_logger().info(
            f"Looking up player by shirt number {card.player_number} in game calls"
        )
        game_calls = (
            await db.db["game_calls"]
            .find({"_id": {"$in": [game.get("home_call"), game.get("away_call")]}})
            .to_list(2)
        )

        if len(game_calls) != 2:
            raise Error.game_calls_not_delivered()

        team_call = None
        for call in game_calls:
            if str(call.get("team")) == str(card.team):
                team_call = call
                break

        if not team_call:
            raise Error.bad_request("Chamada de jogo não encontrada para esta equipa")

        player_found = False
        for p in team_call.get("players", []):
            if p.get("number") == card.player_number:
                player_id = p.get("player")
                player_found = True
                break

        if not player_found or not player_id:
            raise Error.bad_request(
                f"Jogador com número {card.player_number} não encontrado na chamada"
            )

        player = await db.db["players"].find_one({"_id": player_id})
        if player:
            player_name = player["name"]
            player_id = str(player_id)
        else:
            player_id = str(player_id)
    elif card.staff_id:
        staff = await db.db["staff"].find_one({"_id": ObjectId(card.staff_id)})
        if staff:
            staff_name = staff["name"]
            staff_type = staff.get("staff_type")

    get_logger().info(f"Recording {card.card.value} card at minute {card.minute}")
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
            "player_id": player_id,
            "player_name": player_name,
            "player_number": card.player_number,
            "staff_id": card.staff_id,
            "staff_name": staff_name,
            "staff_type": staff_type,
            "team_name": team["name"],
            "period": game.get("current_period", 0),
            "minute": card.minute,
            "card": card.card.value,
            "timestamp": card_dict["timestamp"].isoformat(),
        }
    }

    await add_game_event(ObjectId(card.game), event)
    get_logger().info(
        f"[{current_user['username']}] {card.card.value} card recorded successfully"
    )

    return {"message": "Card assigned successfully"}
