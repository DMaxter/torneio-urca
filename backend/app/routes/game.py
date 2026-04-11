from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime
from database import (
    db,
    GAMES_COLLECTION,
    GAME_CALLS_COLLECTION,
    TOURNAMENTS_COLLECTION,
)
from app.schemas.schemas import (
    CreateGameDto,
    GameDto,
    GameCallDto,
    UpdateGameDto,
    UpdateGameCallDto,
    UpdateGameStatusDto,
    ConfirmGameCallDto,
    UpdatePeriodDto,
)
from app.models.models import GameStatus, GamePhase
from app.error import Error
from app.utils.auth import (
    get_current_user,
    get_user_from_db,
    require_manage_games,
    require_manage_game_events,
    require_game_access,
    require_call_access,
    require_start_game,
)
from app.schemas.schemas import UserRoles
from fastapi import HTTPException, status
from app.utils import get_logger, sanitize_for_serialization

router = APIRouter(prefix="/games", tags=["Games"])


async def check_call_permission(current_user: dict, game_id: str) -> None:
    """Check if user can modify game call: needs manage_games OR (fill_game_calls + game assigned)."""
    if current_user.get("username") == "admin":
        return

    db_user = await get_user_from_db(current_user["username"])
    user_roles = db_user.get("roles", [])

    has_manage_games = UserRoles.MANAGE_GAMES in user_roles
    has_fill_calls = UserRoles.FILL_GAME_CALLS in user_roles
    game_assigned = game_id in db_user.get("assigned_games_for_calls", [])

    if not (has_manage_games or (has_fill_calls and game_assigned)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Sem permissão para gerir chamadas deste jogo"},
        )


async def check_game_permission(current_user: dict, game_id: str) -> None:
    """Check if user can manage game events: needs manage_games OR (manage_game_events + game assigned)."""
    if current_user.get("username") == "admin":
        return

    db_user = await get_user_from_db(current_user["username"])
    user_roles = db_user.get("roles", [])

    has_manage_games = UserRoles.MANAGE_GAMES in user_roles
    has_game_events = UserRoles.MANAGE_GAME_EVENTS in user_roles
    game_assigned = game_id in db_user.get("assigned_games", [])

    if not (has_manage_games or (has_game_events and game_assigned)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Sem permissão para gerir eventos deste jogo"},
        )


def game_call_to_dto(call: dict) -> GameCallDto:
    players = call.get("players", [])
    players_dto = []
    for p in players:
        if isinstance(p, dict):
            players_dto.append(
                {"player": str(p.get("player", "")), "number": p.get("number")}
            )
        else:
            players_dto.append({"player": str(p), "number": None})
    return GameCallDto(
        id=str(call["_id"]),
        game=str(call.get("game", "")),
        team=str(call["team"]),
        players=players_dto,
        deputy=str(call["deputy"]) if call.get("deputy") else None,
    )


def sanitize_for_serialization(obj):
    """Recursively convert ObjectId and datetime to JSON-safe types."""
    if isinstance(obj, dict):
        return {k: sanitize_for_serialization(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_serialization(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def game_to_dto(game: dict, home_call: dict | None, away_call: dict | None) -> GameDto:
    clean_game = sanitize_for_serialization(game)
    clean_home = sanitize_for_serialization(home_call) if home_call else None
    clean_away = sanitize_for_serialization(away_call) if away_call else None

    return GameDto(
        id=clean_game["_id"],
        tournament=clean_game["tournament"],
        scheduled_date=clean_game.get("scheduled_date"),
        start_date=clean_game.get("start_date"),
        finish_date=clean_game.get("finish_date"),
        status=clean_game.get("status", GameStatus.Scheduled),
        phase=clean_game.get("phase", GamePhase.Group),
        home_placeholder=clean_game.get("home_placeholder"),
        away_placeholder=clean_game.get("away_placeholder"),
        home_call=game_call_to_dto(clean_home) if clean_home else None,
        away_call=game_call_to_dto(clean_away) if clean_away else None,
        events=clean_game.get("events", []),
        current_period=clean_game.get("current_period", 0),
        period_elapsed_seconds=clean_game.get("period_elapsed_seconds", 0),
        timer_active=clean_game.get("timer_active", False),
        timer_started_at=clean_game.get("timer_started_at"),
    )


@router.post("", response_model=GameDto, status_code=201)
async def add_game(game: CreateGameDto, current_user=Depends(require_manage_games)):
    from app.routes.tournament import get_tournament

    get_logger().info(
        f"[{current_user['username']}] Creating game for tournament '{game.tournament}'"
    )
    tournament = await get_tournament(game.tournament)

    game_dict = {
        "tournament": ObjectId(game.tournament),
        "scheduled_date": game.scheduled_date,
        "status": GameStatus.Scheduled,
        "phase": game.phase,
        "home_placeholder": game.home_placeholder,
        "away_placeholder": game.away_placeholder,
        "current_period": 0,
        "period_elapsed_minutes": 0,
        "period_elapsed_seconds": 0,
        "timer_active": False,
        "timer_started_at": None,
        "events": [],
    }

    home_call_dict = None
    away_call_dict = None

    if game.home_call and game.away_call:
        home_team = await db.db["teams"].find_one(
            {"_id": ObjectId(game.home_call.team)}
        )
        away_team = await db.db["teams"].find_one(
            {"_id": ObjectId(game.away_call.team)}
        )

        home_players = (
            [{"player": pid, "number": None} for pid in home_team.get("players", [])]
            if home_team
            else []
        )
        away_players = (
            [{"player": pid, "number": None} for pid in away_team.get("players", [])]
            if away_team
            else []
        )

        home_call_dict = {
            "team": ObjectId(game.home_call.team),
            "players": home_players,
            "deputy": None,
        }
        away_call_dict = {
            "team": ObjectId(game.away_call.team),
            "players": away_players,
            "deputy": None,
        }

        get_logger().info("Creating game calls with all team players")
        home_result = await db.db[GAME_CALLS_COLLECTION].insert_one(home_call_dict)
        away_result = await db.db[GAME_CALLS_COLLECTION].insert_one(away_call_dict)

        game_dict["home_call"] = home_result.inserted_id
        game_dict["away_call"] = away_result.inserted_id

    result = await db.db[GAMES_COLLECTION].insert_one(game_dict)

    if home_call_dict and away_call_dict:
        get_logger().info("Linking game calls to game")
        await db.db[GAME_CALLS_COLLECTION].update_many(
            {"_id": {"$in": [game_dict["home_call"], game_dict["away_call"]]}},
            {"$set": {"game": result.inserted_id}},
        )
        home_call_dict["_id"] = game_dict["home_call"]
        away_call_dict["_id"] = game_dict["away_call"]
        home_call_dict["game"] = result.inserted_id
        away_call_dict["game"] = result.inserted_id

    get_logger().info(f"Adding game to tournament '{tournament['name']}'")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"games": result.inserted_id}}
    )

    game_dict["_id"] = result.inserted_id
    get_logger().info(f"[{current_user['username']}] Game created successfully")
    return game_to_dto(game_dict, home_call_dict, away_call_dict)


@router.get("", response_model=List[GameDto])
async def get_games():
    get_logger().info("Retrieving all games")
    games = await db.db[GAMES_COLLECTION].find().to_list(1000)
    calls = await db.db[GAME_CALLS_COLLECTION].find().to_list(1000)

    calls_map = {str(c["_id"]): c for c in calls}

    result = []
    for game in games:
        phase = game.get("phase") or GamePhase.Group
        home_call = (
            calls_map.get(str(game.get("home_call"))) if game.get("home_call") else None
        )
        away_call = (
            calls_map.get(str(game.get("away_call"))) if game.get("away_call") else None
        )
        # Only skip group games where calls exist in DB but can't be found (broken refs)
        # Games without calls (knockout phase) or with valid calls are always included
        if (
            phase == GamePhase.Group
            and game.get("home_call")
            and not (home_call and away_call)
        ):
            continue
        result.append(game_to_dto(game, home_call, away_call))

    get_logger().info(f"Retrieved {len(result)} games")
    return result


@router.get("/{game_id}", response_model=GameDto)
async def get_game_by_id(game_id: str):
    get_logger().info(f"Retrieving game {game_id}")
    game = await get_game(game_id)
    home_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("home_call")})
        if game.get("home_call")
        else None
    )
    away_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("away_call")})
        if game.get("away_call")
        else None
    )
    return game_to_dto(game, home_call, away_call)


@router.patch("/{game_id}", response_model=GameDto)
async def update_game(
    game_id: str, body: UpdateGameDto, current_user=Depends(require_manage_games)
):
    game = await get_game(game_id)
    await db.db[GAMES_COLLECTION].update_one(
        {"_id": game["_id"]},
        {"$set": {"scheduled_date": body.scheduled_date}},
    )
    game["scheduled_date"] = body.scheduled_date
    home_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("home_call")})
        if game.get("home_call")
        else None
    )
    away_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("away_call")})
        if game.get("away_call")
        else None
    )
    return game_to_dto(game, home_call, away_call)


@router.delete("/{game_id}", status_code=204)
async def delete_game(game_id: str, current_user=Depends(require_manage_game_events)):
    game = await get_game(game_id)
    await db.db[GAME_CALLS_COLLECTION].delete_many(
        {"_id": {"$in": [game.get("home_call"), game.get("away_call")]}}
    )
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": game["tournament"]}, {"$pull": {"games": game["_id"]}}
    )
    await db.db[GAMES_COLLECTION].delete_one({"_id": game["_id"]})
    get_logger().info(f"[{current_user['username']}] Deleted game '{game_id}'")


@router.patch("/{game_id}/status", response_model=GameDto)
async def update_game_status(
    game_id: str, body: UpdateGameStatusDto, current_user=Depends(get_current_user)
):
    game = await get_game(game_id)
    current_status = game.get("status", GameStatus.Scheduled)
    new_status = body.status

    # Check permissions based on target status
    if new_status == GameStatus.CallsPending or new_status == GameStatus.ReadyToStart:
        await check_call_permission(current_user, game_id)
    elif new_status == GameStatus.InProgress or new_status == GameStatus.Finished:
        await check_game_permission(current_user, game_id)
    elif new_status == GameStatus.Canceled:
        await check_call_permission(current_user, game_id)
    else:
        raise HTTPException(status_code=400, detail="Transição inválida")

    valid_transitions = {
        GameStatus.Scheduled: [GameStatus.CallsPending, GameStatus.Canceled],
        GameStatus.CallsPending: [GameStatus.ReadyToStart, GameStatus.Canceled],
        GameStatus.ReadyToStart: [GameStatus.InProgress, GameStatus.Canceled],
        GameStatus.InProgress: [GameStatus.Finished],
        GameStatus.Finished: [],
        GameStatus.Canceled: [],
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise Error.bad_request(
            f"Transição inválida de {current_status} para {new_status}"
        )

    await db.db[GAMES_COLLECTION].update_one(
        {"_id": game["_id"]}, {"$set": {"status": new_status}}
    )
    game["status"] = new_status

    if new_status == GameStatus.InProgress:
        game["start_date"] = datetime.utcnow()
        await db.db[GAMES_COLLECTION].update_one(
            {"_id": game["_id"]}, {"$set": {"start_date": game["start_date"]}}
        )

    if new_status == GameStatus.Finished:
        game["finish_date"] = datetime.utcnow()
        await db.db[GAMES_COLLECTION].update_one(
            {"_id": game["_id"]}, {"$set": {"finish_date": game["finish_date"]}}
        )

    get_logger().info(
        f"[{current_user['username']}] Updated game '{game_id}' status to {new_status}"
    )

    home_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("home_call")})
        if game.get("home_call")
        else None
    )
    away_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("away_call")})
        if game.get("away_call")
        else None
    )
    return game_to_dto(game, home_call, away_call)


@router.patch("/{game_id}/confirm-calls", response_model=GameDto)
async def confirm_game_calls(game_id: str, current_user=Depends(get_current_user)):
    await check_call_permission(current_user, game_id)
    game = await get_game(game_id)

    if game.get("status") != GameStatus.CallsPending:
        raise Error.bad_request(
            "As chamadas só podem ser confirmadas quando o jogo está em estado de Chamadas Pendentes"
        )

    home_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("home_call")})
        if game.get("home_call")
        else None
    )
    away_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("away_call")})
        if game.get("away_call")
        else None
    )

    MIN_PLAYERS = 5

    def count_active_players(call):
        if not call:
            return 0
        return sum(1 for p in call.get("players", []) if p.get("number") is not None)

    def check_duplicate_numbers(call):
        if not call:
            return []
        numbers = [
            p.get("number")
            for p in call.get("players", [])
            if p.get("number") is not None
        ]
        duplicates = [n for n in numbers if numbers.count(n) > 1]
        return list(set(duplicates))

    home_count = count_active_players(home_call)
    away_count = count_active_players(away_call)

    if home_count < MIN_PLAYERS:
        raise Error.bad_request(
            f"A equipa da casa precisa de pelo menos {MIN_PLAYERS} jogadores com número atribuído. Atual: {home_count}"
        )
    if away_count < MIN_PLAYERS:
        raise Error.bad_request(
            f"A equipa visitante precisa de pelo menos {MIN_PLAYERS} jogadores com número atribuído. Atual: {away_count}"
        )

    home_duplicates = check_duplicate_numbers(home_call)
    if home_duplicates:
        raise Error.bad_request(
            f"A equipa da casa tem números duplicados: {', '.join(map(str, home_duplicates))}"
        )

    away_duplicates = check_duplicate_numbers(away_call)
    if away_duplicates:
        raise Error.bad_request(
            f"A equipa visitante tem números duplicados: {', '.join(map(str, away_duplicates))}"
        )

    await db.db[GAMES_COLLECTION].update_one(
        {"_id": game["_id"]}, {"$set": {"status": GameStatus.ReadyToStart}}
    )
    game["status"] = GameStatus.ReadyToStart

    get_logger().info(
        f"[{current_user['username']}] Confirmed calls for game '{game_id}'"
    )

    return game_to_dto(game, home_call, away_call)


@router.patch("/{game_id}/period", response_model=GameDto)
async def update_period(
    game_id: str, body: UpdatePeriodDto, current_user=Depends(get_current_user)
):
    get_logger().info(
        f"[{current_user['username']}] Updating period for game '{game_id}': action={body.action}, period={body.period}, seconds={getattr(body, 'seconds', None)}"
    )
    game = await get_game(game_id)

    if game.get("status") != GameStatus.InProgress:
        raise Error.bad_request("O jogo não está em progresso")

    updates = {}
    now = datetime.utcnow()
    current_period = game.get("current_period", 0)
    period_elapsed_seconds = game.get("period_elapsed_seconds", 0)
    timer_active = game.get("timer_active", False)
    timer_started_at = game.get("timer_started_at")

    if body.action == "start_new":
        if body.period is not None:
            new_period = body.period
        elif current_period == 0:
            new_period = 1
        else:
            # Period already set (e.g., by "end" action), just start the timer
            new_period = current_period

        # Validate tie for overtime (period 3) and penalties (period 5)
        if new_period in (3, 5):
            home_call_doc = (
                await db.db[GAME_CALLS_COLLECTION].find_one(
                    {"_id": game.get("home_call")}
                )
                if game.get("home_call")
                else None
            )
            away_call_doc = (
                await db.db[GAME_CALLS_COLLECTION].find_one(
                    {"_id": game.get("away_call")}
                )
                if game.get("away_call")
                else None
            )
            if not home_call_doc or not away_call_doc:
                raise Error.bad_request("Game calls not found")
            home_team_id = str(home_call_doc["team"])
            away_team_id = str(away_call_doc["team"])
            home_goals = 0
            away_goals = 0
            for e in game.get("events", []):
                if "Goal" in e:
                    goal = e["Goal"]
                    # Only count goals from completed periods (before this new period)
                    if goal.get("period", 0) < new_period:
                        team_id = str(goal.get("team_id"))
                        if team_id == home_team_id:
                            home_goals += 1
                        elif team_id == away_team_id:
                            away_goals += 1
            if home_goals != away_goals:
                if new_period == 3:
                    raise Error.bad_request(
                        "Scores must be tied to proceed to overtime"
                    )
                else:
                    raise Error.bad_request(
                        "Scores must be tied to proceed to penalties"
                    )

        updates["current_period"] = new_period
        updates["period_elapsed_seconds"] = 0
        updates["timer_active"] = True
        updates["timer_started_at"] = now
    elif body.action == "resume":
        if timer_active:
            raise Error.bad_request("Timer is already active")
        updates["timer_active"] = True
        updates["timer_started_at"] = now
    elif body.action == "stop":
        if not timer_active:
            raise Error.bad_request("Timer is not active")
        if timer_started_at:
            elapsed_since_start = int((now - timer_started_at).total_seconds())
            updates["period_elapsed_seconds"] = (
                period_elapsed_seconds + elapsed_since_start
            )
        updates["timer_active"] = False
        updates["timer_started_at"] = None
    elif body.action == "end":
        new_period = current_period + 1
        # Validate tie for overtime (period 3) and penalties (period 5)
        if new_period in (3, 5):
            home_call_doc = (
                await db.db[GAME_CALLS_COLLECTION].find_one(
                    {"_id": game.get("home_call")}
                )
                if game.get("home_call")
                else None
            )
            away_call_doc = (
                await db.db[GAME_CALLS_COLLECTION].find_one(
                    {"_id": game.get("away_call")}
                )
                if game.get("away_call")
                else None
            )
            if not home_call_doc or not away_call_doc:
                raise Error.bad_request("Game calls not found")
            home_team_id = str(home_call_doc["team"])
            away_team_id = str(away_call_doc["team"])
            home_goals = 0
            away_goals = 0
            for e in game.get("events", []):
                if "Goal" in e:
                    goal = e["Goal"]
                    if goal.get("period", 0) < new_period:
                        team_id = str(goal.get("team_id"))
                        if team_id == home_team_id:
                            home_goals += 1
                        elif team_id == away_team_id:
                            away_goals += 1
            if home_goals != away_goals:
                if new_period == 3:
                    raise Error.bad_request(
                        "Scores must be tied to proceed to overtime"
                    )
                else:
                    raise Error.bad_request(
                        "Scores must be tied to proceed to penalties"
                    )
        updates["current_period"] = new_period
        updates["period_elapsed_seconds"] = 0
        updates["timer_active"] = False
        updates["timer_started_at"] = None
    elif body.action == "set_seconds":
        if body.seconds is None:
            raise Error.bad_request("Seconds is required")
        if body.seconds < 0 or body.seconds > 1200:
            raise Error.bad_request("Seconds must be between 0 and 1200")
        if timer_active:
            raise Error.bad_request(
                "Cannot set seconds while timer is active. Stop the timer first."
            )
        updates["period_elapsed_seconds"] = body.seconds
    else:
        raise Error.bad_request(f"Invalid action: {body.action}")

    # Capture values before update for event creation
    old_period = game.get("current_period", 0)
    old_elapsed = game.get("period_elapsed_seconds", 0)

    await db.db[GAMES_COLLECTION].update_one({"_id": game["_id"]}, {"$set": updates})

    game.update(updates)

    # Add period start/end events
    if body.action == "start_new":
        period_num = updates.get("current_period", old_period)
        # If there was a previous period running, auto-end it
        if old_period > 0 and old_period != period_num:
            end_event = {
                "PeriodEnd": {
                    "period": old_period,
                    "elapsed_seconds": old_elapsed,
                    "timestamp": now.isoformat(),
                }
            }
            await add_game_event(game["_id"], end_event)
        start_event = {
            "PeriodStart": {
                "period": period_num,
                "timestamp": now.isoformat(),
            }
        }
        await add_game_event(game["_id"], start_event)
    elif body.action == "resume":
        period_num = game.get("current_period", 0)
        resume_event = {
            "PeriodResume": {
                "period": period_num,
                "timestamp": now.isoformat(),
            }
        }
        await add_game_event(game["_id"], resume_event)
    elif body.action == "stop":
        stop_event = {
            "PeriodPause": {
                "period": game.get("current_period", 0),
                "elapsed_seconds": updates.get(
                    "period_elapsed_seconds", game.get("period_elapsed_seconds", 0)
                ),
                "timestamp": now.isoformat(),
            }
        }
        await add_game_event(game["_id"], stop_event)
    elif body.action == "end":
        # The period being ended is the one that was running before the update
        end_event = {
            "PeriodEnd": {
                "period": old_period,
                "elapsed_seconds": old_elapsed,
                "timestamp": now.isoformat(),
            }
        }
        await add_game_event(game["_id"], end_event)

    home_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("home_call")})
        if game.get("home_call")
        else None
    )
    away_call = (
        await db.db[GAME_CALLS_COLLECTION].find_one({"_id": game.get("away_call")})
        if game.get("away_call")
        else None
    )
    return game_to_dto(game, home_call, away_call)


@router.delete("/{game_id}/events/{event_index}", status_code=204)
async def delete_game_event(
    game_id: str, event_index: int, _=Depends(require_manage_game_events)
):
    """Delete a specific game event by its index in the events list."""
    get_logger().info(
        f"[{current_user['username']}] Deleting event {event_index} from game '{game_id}'"
    )
    try:
        game = await db.db[GAMES_COLLECTION].find_one({"_id": ObjectId(game_id)})
    except Exception:
        raise Error.invalid_id("game")
    if not game:
        raise Error.not_found("Game")

    events = game.get("events", [])
    if event_index < 0 or event_index >= len(events):
        raise Error.bad_request("Invalid event index")

    events.pop(event_index)
    await db.db[GAMES_COLLECTION].update_one(
        {"_id": ObjectId(game_id)}, {"$set": {"events": events}}
    )
    get_logger().info(f"Event {event_index} deleted from game '{game_id}'")


@router.patch("/calls/{call_id}", response_model=GameCallDto)
async def update_game_call(
    call_id: str, body: UpdateGameCallDto, current_user=Depends(get_current_user)
):
    try:
        call = await db.db[GAME_CALLS_COLLECTION].find_one({"_id": ObjectId(call_id)})
    except Exception:
        raise Error.invalid_id("game call")
    if not call:
        raise Error.not_found("Game call")

    game_id = str(call.get("game"))
    await check_call_permission(current_user, game_id)

    players_to_store = []
    for p in body.players:
        player_entry = {"player": ObjectId(p["player"]), "number": p.get("number")}
        players_to_store.append(player_entry)

    await db.db[GAME_CALLS_COLLECTION].update_one(
        {"_id": call["_id"]}, {"$set": {"players": players_to_store}}
    )

    get_logger().info(f"[{current_user['username']}] Updated game call '{call_id}'")
    call["players"] = players_to_store
    return game_call_to_dto(call)


@router.patch("/calls/{call_id}/populate", response_model=GameCallDto)
async def populate_game_call(call_id: str, current_user=Depends(get_current_user)):
    try:
        call = await db.db[GAME_CALLS_COLLECTION].find_one({"_id": ObjectId(call_id)})
    except Exception:
        raise Error.invalid_id("game call")
    if not call:
        raise Error.not_found("Game call")

    game_id = str(call.get("game"))
    await check_call_permission(current_user, game_id)

    team = await db.db["teams"].find_one({"_id": call["team"]})
    if not team:
        raise Error.not_found("Team")

    players = [{"player": pid, "number": None} for pid in team.get("players", [])]

    await db.db[GAME_CALLS_COLLECTION].update_one(
        {"_id": call["_id"]}, {"$set": {"players": players}}
    )

    get_logger().info(
        f"[{current_user['username']}] Populated game call '{call_id}' with team players"
    )
    call["players"] = players
    return game_call_to_dto(call)


async def get_game(game_id: str) -> dict:
    try:
        game = await db.db[GAMES_COLLECTION].find_one({"_id": ObjectId(game_id)})
    except Exception:
        raise Error.invalid_id("game")
    if not game:
        raise Error.not_found("Game")
    return game


def check_game_running(tournament_id: ObjectId, game: dict) -> None:
    if game["tournament"] != tournament_id:
        raise Error.game_not_in_tournament()
    if game.get("status") != GameStatus.InProgress:
        raise Error.game_not_in_progress()


async def add_game_event(game_id: ObjectId, event: dict) -> None:
    await db.db[GAMES_COLLECTION].update_one(
        {"_id": game_id}, {"$push": {"events": event}}
    )
