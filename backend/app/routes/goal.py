from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime
from database import db, GOALS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignGoalDto
from app.models.models import GameStatus
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger
from app.routes.tournament import get_tournament
from app.routes.game import get_game, add_game_event
from app.routes.team import get_team

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", status_code=201)
async def assign_goal(goal: AssignGoalDto, current_user=Depends(get_current_user)):
    get_logger().info(
        f"[{current_user['username']}] Assigning goal - player_number: {goal.player_number}, game: {goal.game}, minute: {goal.minute}"
    )
    tournament = await get_tournament(goal.tournament)
    game = await get_game(goal.game)

    if game.get("status") != GameStatus.InProgress:
        raise Error.bad_request("O jogo não está em progresso")

    get_logger().info(f"Validating team '{goal.team}'")
    team = await get_team(goal.team)

    player_name = ""
    player_id = None

    if goal.player_number is not None:
        get_logger().info(
            f"Looking up player by shirt number {goal.player_number} in game calls"
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
            if str(call.get("team")) == str(goal.team):
                team_call = call
                break

        if not team_call:
            raise Error.bad_request("Chamada de jogo não encontrada para esta equipa")

        player_found = False
        for p in team_call.get("players", []):
            if p.get("number") == goal.player_number:
                player_id = p.get("player")
                player_found = True
                break

        if not player_found or not player_id:
            raise Error.bad_request(
                f"Jogador com número {goal.player_number} não encontrado na chamada"
            )

        player = await db.db["players"].find_one({"_id": player_id})
        if player:
            player_name = player["name"]
            player_id = str(player_id)
        else:
            player_id = str(player_id)

    get_logger().info(
        f"Recording goal for player number {goal.player_number} at minute {goal.minute}"
    )
    goal_dict = {
        "tournament": ObjectId(goal.tournament),
        "team_id": ObjectId(goal.team),
        "team_name": team["name"],
        "player_id": ObjectId(player_id) if player_id else None,
        "player_name": player_name,
        "player_number": goal.player_number,
        "staff_id": ObjectId(goal.staff_id) if goal.staff_id else None,
        "staff_name": "",
        "staff_type": None,
        "game_id": ObjectId(goal.game),
        "period": game.get("current_period", 0),
        "minute": goal.minute,
        "timestamp": datetime.utcnow(),
    }

    result = await db.db[GOALS_COLLECTION].insert_one(goal_dict)
    goal_dict["_id"] = result.inserted_id

    get_logger().info("Updating tournament with goal")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"goals": goal_dict}}
    )

    get_logger().info("Adding goal event to game")
    event = {
        "Goal": {
            "player_id": player_id,
            "player_name": player_name,
            "player_number": goal.player_number,
            "team_name": team["name"],
            "period": game.get("current_period", 0),
            "minute": goal.minute,
            "timestamp": goal_dict["timestamp"].isoformat(),
        }
    }

    await add_game_event(ObjectId(goal.game), event)
    get_logger().info(
        f"[{current_user['username']}] Goal for player number {goal.player_number} recorded successfully"
    )

    return {"message": "Goal assigned successfully"}
