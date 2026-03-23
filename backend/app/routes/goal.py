from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime
from database import db, GOALS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import AssignGoalDto
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger
from app.routes.tournament import get_tournament
from app.routes.game import get_game, check_game_running, add_game_event
from app.routes.team import get_team
from app.routes.player import get_player

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", status_code=201)
async def assign_goal(goal: AssignGoalDto, current_user=Depends(get_current_user)):
    get_logger().info(
        f"[{current_user['username']}] Assigning goal - player: {goal.player}, game: {goal.game}, minute: {goal.minute}"
    )
    tournament = await get_tournament(goal.tournament)
    game = await get_game(goal.game)

    tournament_id = ObjectId(goal.tournament)
    get_logger().info("Checking if game is running")
    check_game_running(tournament_id, game)

    get_logger().info(f"Validating player '{goal.player}' in team '{goal.team}'")
    team = await get_team(goal.team)
    player = await get_player(goal.player)

    player_id = ObjectId(goal.player)
    if player_id not in team.get("players", []):
        raise Error.player_not_in_team()

    get_logger().info("Checking if player is in game calls")
    game_calls = (
        await db.db["game_calls"]
        .find({"_id": {"$in": [game.get("home_call"), game.get("away_call")]}})
        .to_list(2)
    )

    if len(game_calls) != 2:
        raise Error.game_calls_not_delivered()

    player_oid = ObjectId(goal.player)
    in_game = False
    for call in game_calls:
        if player_oid in call.get("players", []):
            in_game = True
            break

    if not in_game:
        raise Error.player_not_in_game()

    get_logger().info(
        f"Recording goal for player '{player['name']}' at minute {goal.minute}"
    )
    goal_dict = {
        "tournament": ObjectId(goal.tournament),
        "team_id": ObjectId(goal.team),
        "team_name": team["name"],
        "player_id": ObjectId(goal.player),
        "player_name": player["name"],
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
            "player_id": str(ObjectId(goal.player)),
            "player_name": player["name"],
            "team_name": team["name"],
            "period": game.get("current_period", 0),
            "minute": goal.minute,
            "timestamp": goal_dict["timestamp"].isoformat(),
        }
    }

    await add_game_event(ObjectId(goal.game), event)
    get_logger().info(
        f"[{current_user['username']}] Goal for player '{player['name']}' recorded successfully"
    )

    return {"message": "Goal assigned successfully"}
