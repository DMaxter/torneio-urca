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

    if not goal.own_goal and goal.player_number is not None:
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

        # Build map of team_id -> call
        team_calls = {}
        for call in game_calls:
            team_id = str(call.get("team"))
            team_calls[team_id] = call

        scoring_team_id = str(goal.team)
        if scoring_team_id not in team_calls:
            raise Error.bad_request(
                "Chamada de jogo não encontrada para a equipa que marcou"
            )

        # Regular goal: player is from scoring team
        team_call = team_calls[scoring_team_id]

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

    # For own goals, the team credited is the opposing team (not the team whose button was clicked)
    committing_team_id = goal.team
    committing_team_name = team["name"]

    if goal.own_goal:
        # Find the opposing team by comparing with the game's home_call and away_call team IDs
        home_call = (
            await db.db["game_calls"].find_one({"_id": game.get("home_call")})
            if game.get("home_call")
            else None
        )
        away_call = (
            await db.db["game_calls"].find_one({"_id": game.get("away_call")})
            if game.get("away_call")
            else None
        )

        scoring_team_id = str(goal.team)
        if home_call and str(home_call.get("team")) != scoring_team_id:
            # Opposing team is home team
            credited_team_id = str(home_call.get("team"))
            credited_team = await db.db["teams"].find_one(
                {"_id": home_call.get("team")}
            )
            credited_team_name = credited_team["name"] if credited_team else ""
        elif away_call and str(away_call.get("team")) != scoring_team_id:
            # Opposing team is away team
            credited_team_id = str(away_call.get("team"))
            credited_team = await db.db["teams"].find_one(
                {"_id": away_call.get("team")}
            )
            credited_team_name = credited_team["name"] if credited_team else ""
        else:
            # Fallback: use the team as-is
            credited_team_id = goal.team
            credited_team_name = team["name"]
            get_logger().warning(
                f"Could not determine opposing team for own goal, using {credited_team_name}"
            )
    else:
        credited_team_id = goal.team
        credited_team_name = team["name"]

    # Calculate live elapsed seconds if timer is active
    current_elapsed = game.get("period_elapsed_seconds", 0)
    if game.get("timer_active") and game.get("timer_started_at"):
        now_utc = datetime.utcnow()
        # Ensure timer_started_at is compared correctly
        active_elapsed = int((now_utc - game["timer_started_at"]).total_seconds())
        current_elapsed += active_elapsed

    event_second = goal.second if goal.second is not None else (current_elapsed % 60)

    goal_dict = {
        "tournament": ObjectId(goal.tournament),
        "team_id": ObjectId(credited_team_id),
        "team_name": credited_team_name,
        "player_id": ObjectId(player_id) if (player_id and not goal.own_goal) else None,
        "player_name": player_name if not goal.own_goal else None,
        "player_number": goal.player_number if not goal.own_goal else None,
        "own_goal": goal.own_goal,
        "game_id": ObjectId(goal.game),
        "period": game.get("current_period", 0),
        "minute": goal.minute,
        "second": event_second,
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
            "player_id": player_id if not goal.own_goal else None,
            "player_name": player_name if not goal.own_goal else None,
            "player_number": goal.player_number if not goal.own_goal else None,
            "team_name": credited_team_name,
            "own_goal": goal.own_goal,
            "own_goal_committed_by": committing_team_name if goal.own_goal else None,
            "period": game.get("current_period", 0),
            "minute": goal.minute,
            "second": event_second,
            "timestamp": goal_dict["timestamp"].isoformat(),
        }
    }

    await add_game_event(ObjectId(goal.game), event)
    get_logger().info(
        f"[{current_user['username']}] Goal for player number {goal.player_number} recorded successfully"
    )

    return {"message": "Goal assigned successfully"}
