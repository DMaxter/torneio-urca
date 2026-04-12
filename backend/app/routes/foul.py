from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime
from database import db, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignFoulDto
from app.models.models import GameStatus, StaffType
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger
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
    game_calls = (
        await db.db["game_calls"]
        .find({"_id": {"$in": [game.get("home_call"), game.get("away_call")]}})
        .to_list(2)
    )

    if len(game_calls) != 2:
        raise Error.game_calls_not_delivered()

    team_call = None
    for call in game_calls:
        if str(call.get("team")) == str(foul.team):
            team_call = call
            break

    if not team_call:
        raise Error.bad_request("Chamada de jogo não encontrada para esta equipa")

    if foul.player_number is not None:
        player_found = False
        for p in team_call.get("players", []):
            if p.get("number") == foul.player_number:
                player_id = p.get("player")
                player_found = True
                break

        if not player_found or not player_id:
            raise Error.bad_request(
                f"Jogador com número {foul.player_number} não encontrado na chamada"
            )

        player = await db.db["players"].find_one({"_id": player_id})
        if player:
            player_name = player["name"]
            player_id = str(player_id)
        else:
            player_id = str(player_id)
    elif foul.staff_id:
        staff_found = False
        for s_id in team_call.get("staff", []):
            if str(s_id) == str(foul.staff_id):
                staff_found = True
                break

        if not staff_found:
            raise Error.bad_request("Membro do staff não encontrado na chamada deste jogo")

        staff = await db.db["staff"].find_one({"_id": ObjectId(foul.staff_id)})
        if staff:
            staff_name = staff["name"]
            staff_type = staff.get("staff_type")

    get_logger().info(f"Recording foul at minute {foul.minute}")
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
        "second": game.get("period_elapsed_seconds", 0) % 60,
        "timestamp": datetime.utcnow(),
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
            "second": game.get("period_elapsed_seconds", 0) % 60,
            "card": None,
            "timestamp": foul_dict["timestamp"].isoformat(),
        }
    }

    await add_game_event(ObjectId(foul.game), event)
    get_logger().info(f"[{current_user['username']}] Foul recorded successfully")

    return {"message": "Foul assigned successfully"}
