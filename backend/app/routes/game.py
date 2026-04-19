from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from database import (
    db,
    GAMES_COLLECTION,
    GAME_CALLS_COLLECTION,
    TOURNAMENTS_COLLECTION,
    TEAMS_COLLECTION,
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
    ManualEventDto,
    AssignPenaltyDto,
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
from app.utils.game_events import get_game_calls_for_team, resolve_player_from_call

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
        team=str(call["team"]) if call.get("team") else None,
        players=players_dto,
        staff=[str(s) for s in call.get("staff", [])],
        deputy=str(call.get("deputy")) if call.get("deputy") else None,
    )



def game_to_dto(game: dict, home_call: dict | None, away_call: dict | None) -> GameDto:
    clean_game = sanitize_for_serialization(game)
    clean_home = sanitize_for_serialization(home_call) if home_call else None
    clean_away = sanitize_for_serialization(away_call) if away_call else None

    return GameDto(
        id=clean_game["_id"],
        tournament=clean_game["tournament"],
        label=clean_game.get("label"),
        scheduled_date=clean_game.get("scheduled_date"),
        start_date=clean_game.get("start_date"),
        finish_date=clean_game.get("finish_date"),
        status=clean_game.get("status", GameStatus.Scheduled),
        phase=clean_game.get("phase", GamePhase.Group),
        home_placeholder=clean_game.get("home_placeholder"),
        away_placeholder=clean_game.get("away_placeholder"),
        group=clean_game.get("group"),
        home_group_ref=clean_game.get("home_group_ref"),
        home_group_position=clean_game.get("home_group_position"),
        away_group_ref=clean_game.get("away_group_ref"),
        away_group_position=clean_game.get("away_group_position"),
        home_call=game_call_to_dto(clean_home) if clean_home else None,
        away_call=game_call_to_dto(clean_away) if clean_away else None,
        events=clean_game.get("events", []),
        current_period=clean_game.get("current_period", 0),
        period_elapsed_seconds=clean_game.get("period_elapsed_seconds", 0),
        timer_active=clean_game.get("timer_active", False),
        timer_started_at=clean_game.get("timer_started_at"),
        next_game_winner=clean_game.get("next_game_winner"),
        next_game_loser=clean_game.get("next_game_loser"),
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
        "label": game.label,
        "scheduled_date": game.scheduled_date,
        "status": GameStatus.Scheduled,
        "phase": game.phase,
        "home_placeholder": game.home_placeholder,
        "away_placeholder": game.away_placeholder,
        # Group reference for group phase games
        "group": ObjectId(game.group) if game.group else None,
        # Structured group reference for knockout
        "home_group_ref": ObjectId(game.home_group_ref)
        if game.home_group_ref
        else None,
        "home_group_position": game.home_group_position,
        "away_group_ref": ObjectId(game.away_group_ref)
        if game.away_group_ref
        else None,
        "away_group_position": game.away_group_position,
        "next_game_winner": ObjectId(game.next_game_winner)
        if game.next_game_winner
        else None,
        "next_game_loser": ObjectId(game.next_game_loser)
        if game.next_game_loser
        else None,
        "current_period": 0,
        "period_elapsed_minutes": 0,
        "period_elapsed_seconds": 0,
        "timer_active": False,
        "timer_started_at": None,
        "events": [],
    }

    home_call_dict = None
    away_call_dict = None

    # Always create game calls (for all games - group and knockout)
    if game.home_call and game.away_call:
        # Create with teams (group games with specified teams)
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
            "staff": [],
            "deputy": None,
        }
        away_call_dict = {
            "team": ObjectId(game.away_call.team),
            "players": away_players,
            "staff": [],
            "deputy": None,
        }

        get_logger().info("Creating game calls with all team players")
    else:
        # Create empty game calls (knockout games without resolved teams)
        home_call_dict = {
            "team": None,
            "players": [],
            "staff": [],
            "deputy": None,
        }
        away_call_dict = {
            "team": None,
            "players": [],
            "staff": [],
            "deputy": None,
        }

        get_logger().info("Creating empty game calls for knockout game")

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


async def calculate_game_scores(game: dict) -> tuple[int, int]:
    """Calculate home and away goals for a finished game."""
    home_goals = 0
    away_goals = 0

    for event in game.get("events", []):
        if "Goal" in event:
            goal = event["Goal"]
            team_name = goal.get("team_name", "")

            home_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": game.get("home_call")}
            )
            away_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": game.get("away_call")}
            )

            if home_call and away_call:
                home_team = await db.db[TEAMS_COLLECTION].find_one(
                    {"_id": home_call.get("team")}
                )
                away_team = await db.db[TEAMS_COLLECTION].find_one(
                    {"_id": away_call.get("team")}
                )

                if home_team and team_name == home_team.get("name", ""):
                    home_goals += 1
                elif away_team and team_name == away_team.get("name", ""):
                    away_goals += 1

    return home_goals, away_goals


async def advance_winner_to_next_game(game: dict):
    """Advance winner/loser to next knockout game when a game finishes."""
    if game.get("phase") == GamePhase.Group:
        return

    if not game.get("next_game_winner") and not game.get("next_game_loser"):
        return

    home_goals, away_goals = await calculate_game_scores(game)

    home_call = await db.db[GAME_CALLS_COLLECTION].find_one(
        {"_id": game.get("home_call")}
    )
    away_call = await db.db[GAME_CALLS_COLLECTION].find_one(
        {"_id": game.get("away_call")}
    )

    if not home_call or not away_call:
        return

    winner_call = None
    loser_call = None

    if home_goals > away_goals:
        winner_call = home_call
        loser_call = away_call
    elif away_goals > home_goals:
        winner_call = away_call
        loser_call = home_call
    else:
        get_logger().warning(f"Game '{game.get('_id')}' ended in tie, cannot advance")
        return

    winner_team_id = winner_call.get("team")
    loser_team_id = loser_call.get("team")

    # Advance winner to next game (via direct game call ID)
    if game.get("next_game_winner"):
        # Fetch team players like group→knockout advance (set numbers to None)
        if winner_team_id:
            winner_team = await db.db[TEAMS_COLLECTION].find_one(
                {"_id": winner_team_id}
            )
            players = (
                [{"player": p, "number": None} for p in winner_team.get("players", [])]
                if winner_team
                else []
            )
        else:
            players = []
        await db.db[GAME_CALLS_COLLECTION].update_one(
            {"_id": game.get("next_game_winner")},
            {"$set": {"team": winner_team_id, "players": players, "staff": []}},
        )
        get_logger().info(
            f"Advanced winner to next game (call: {game.get('next_game_winner')})"
        )

    # Advance loser to next game (for third place)
    if game.get("next_game_loser"):
        # Fetch team players like group→knockout advance (set numbers to None)
        if loser_team_id:
            loser_team = await db.db[TEAMS_COLLECTION].find_one({"_id": loser_team_id})
            players = (
                [{"player": p, "number": None} for p in loser_team.get("players", [])]
                if loser_team
                else []
            )
        else:
            players = []
        await db.db[GAME_CALLS_COLLECTION].update_one(
            {"_id": game.get("next_game_loser")},
            {"$set": {"team": loser_team_id, "players": players, "staff": []}},
        )
        get_logger().info(
            f"Advanced loser to next game (call: {game.get('next_game_loser')})"
        )


async def initialize_knockout_dependencies(tournament_id: str):
    """Initialize next_game references based on game labels for knockout phase."""
    games = (
        await db.db[GAMES_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
                "phase": {"$ne": GamePhase.Group},
            }
        )
        .to_list(100)
    )

    # Build a map of game labels to game IDs
    label_map: dict[str, ObjectId] = {}
    for g in games:
        label = g.get("label", "")
        if label:
            label_map[label] = g["_id"]

    # Map of label -> game_id for winners/losers references
    def resolve_ref(text: str) -> ObjectId | None:
        if "Vencedor" in text:
            # Extract game label like "Vencedor Quartos de Final - Jogo 1"
            # or "Vencedor Meia Final - Jogo 1"
            for label, gid in label_map.items():
                if label in text:
                    return gid
        elif "Perdedor" in text:
            for label, gid in label_map.items():
                if label in text:
                    return gid
        return None

    # Update each game with references to next games
    for g in games:
        updates: dict = {}

        home_placeholder = g.get("home_placeholder", "")
        away_placeholder = g.get("away_placeholder", "")

        if home_placeholder and "Vencedor" in home_placeholder:
            next_gid = resolve_ref(home_placeholder)
            if next_gid:
                updates["next_game_home"] = next_gid

        if away_placeholder and "Vencedor" in away_placeholder:
            next_gid = resolve_ref(away_placeholder)
            if next_gid:
                updates["next_game_away"] = next_gid

        # Check label for loser references (third place)
        label = g.get("label") if g.get("label") else ""
        if label and "Meia Final" in label and label in label_map:
            # This SF winner goes to Final, loser goes to 3rd place
            final_label = "Final"
            third_label = "3º e 4º Lugar"

            if final_label in label_map:
                updates["next_game_home"] = label_map[final_label]
            if third_label in label_map:
                updates["next_game_loser"] = label_map[third_label]

        if label and "Quartos de Final" in label:
            # This QF winner goes to SF
            if label in label_map:
                if "Jogo 1" in label or "Jogo 2" in label:
                    # Winners go to SF Jogo 1
                    sf_label = "Meia Final - Jogo 1"
                    if sf_label in label_map:
                        updates["next_game_home"] = label_map[sf_label]
                else:
                    # Winners go to SF Jogo 2
                    sf_label = "Meia Final - Jogo 2"
                    if sf_label in label_map:
                        updates["next_game_home"] = label_map[sf_label]

        if updates:
            await db.db[GAMES_COLLECTION].update_one(
                {"_id": g["_id"]}, {"$set": updates}
            )
            get_logger().info(f"Initialized dependencies for game {label}")


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

    # Validate required fields before allowing CallsPending (blocks all later statuses)
    if new_status == GameStatus.CallsPending:
        if not game.get("scheduled_date"):
            raise Error.bad_request("Não é possível iniciar o jogo sem data atribuída")

        if game.get("phase") and game.get("phase") != GamePhase.Group:
            home_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": game.get("home_call")}
            )
            away_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": game.get("away_call")}
            )
            if not (
                home_call
                and away_call
                and home_call.get("team")
                and away_call.get("team")
            ):
                raise Error.bad_request(
                    "Não é possível iniciar o jogo de eliminatórias sem ambas as equipas atribuídas"
                )

    await db.db[GAMES_COLLECTION].update_one(
        {"_id": game["_id"]}, {"$set": {"status": new_status}}
    )
    game["status"] = new_status

    if new_status == GameStatus.InProgress:
        game["start_date"] = datetime.now(timezone.utc)
        await db.db[GAMES_COLLECTION].update_one(
            {"_id": game["_id"]}, {"$set": {"start_date": game["start_date"]}}
        )

    if new_status == GameStatus.Finished:
        game["finish_date"] = datetime.now(timezone.utc)
        await db.db[GAMES_COLLECTION].update_one(
            {"_id": game["_id"]}, {"$set": {"finish_date": game["finish_date"]}}
        )

        # Auto-advance winner to next game (knockout phase)
        await advance_winner_to_next_game(game)

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
    now = datetime.now(timezone.utc)
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


@router.post("/{game_id}/events", status_code=201)
async def add_manual_game_event(
    game_id: str, body: ManualEventDto, current_user=Depends(require_manage_game_events)
):
    """Add a manual text event at the current game time."""
    get_logger().info(
        f"[{current_user['username']}] Adding manual event to game '{game_id}': {body.description}"
    )
    game = await get_game(game_id)

    if game.get("status") != GameStatus.InProgress:
        raise Error.bad_request("O jogo não está em progresso")

    # Calculate current elapsed seconds
    current_elapsed = game.get("period_elapsed_seconds", 0)
    now = datetime.now(timezone.utc)
    if game.get("timer_active") and game.get("timer_started_at"):
        started = game["timer_started_at"]
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        active_elapsed = int((now - started).total_seconds())
        current_elapsed += active_elapsed

    current_minute = int(current_elapsed // 60)
    current_second = int(current_elapsed % 60)

    manual_event = {
        "Manual": {
            "description": body.description,
            "period": game.get("current_period", 0),
            "minute": current_minute,
            "second": current_second,
            "timestamp": now.isoformat(),
        }
    }

    await add_game_event(game["_id"], manual_event)
    get_logger().info(f"Manual event added to game '{game_id}'")

    return {"message": "Evento manual adicionado"}


@router.delete("/{game_id}/events/{event_index}", status_code=204)
async def delete_game_event(
    game_id: str,
    event_index: int,
    current_user: dict = Depends(require_manage_game_events),
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

    update_fields = {"players": players_to_store}
    if body.staff is not None:
        update_fields["staff"] = [ObjectId(s) for s in body.staff]

    await db.db[GAME_CALLS_COLLECTION].update_one(
        {"_id": call["_id"]}, {"$set": update_fields}
    )

    get_logger().info(f"[{current_user['username']}] Updated game call '{call_id}'")
    call["players"] = players_to_store
    if body.staff is not None:
        call["staff"] = update_fields["staff"]
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

    staff_ids = []
    for role in [
        "main_coach",
        "assistant_coach",
        "physiotherapist",
        "first_deputy",
        "second_deputy",
    ]:
        if team.get(role):
            staff_ids.append(team[role])

    await db.db[GAME_CALLS_COLLECTION].update_one(
        {"_id": call["_id"]}, {"$set": {"players": players, "staff": staff_ids}}
    )

    get_logger().info(
        f"[{current_user['username']}] Populated game call '{call_id}' with team players and staff"
    )
    call["players"] = players
    call["staff"] = staff_ids
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


@router.post("/{game_id}/penalties", status_code=201)
async def assign_penalty(
    game_id: str,
    body: AssignPenaltyDto,
    current_user=Depends(require_manage_game_events),
):
    """Add a penalty event (scored or failed) to the game."""
    get_logger().info(
        f"[{current_user['username']}] Adding penalty event to game '{game_id}': "
        f"team={body.team}, player_number={body.player_number}, scored={body.scored}"
    )
    game = await get_game(game_id)

    if game.get("status") != GameStatus.InProgress:
        raise Error.bad_request("O jogo não está em progresso")

    game_id_pending = game_id  # alias for readability
    team_call, _ = await get_game_calls_for_team(game, body.team)
    player_id_raw, player_name = await resolve_player_from_call(
        team_call, body.player_number
    )

    # Find team name
    team = await db.db["teams"].find_one({"_id": ObjectId(body.team)})
    team_name = team["name"] if team else "Equipa desconhecida"

    now = datetime.now(timezone.utc)
    penalty_event = {
        "Penalty": {
            "player_id": str(player_id_raw),
            "player_name": player_name,
            "player_number": body.player_number,
            "team_id": body.team,
            "team_name": team_name,
            "scored": body.scored,
            "period": game.get("current_period", 0),
            "minute": body.minute,
            "second": body.second if body.second is not None else 0,
            "timestamp": now.isoformat(),
        }
    }

    await add_game_event(game["_id"], penalty_event)
    get_logger().info(f"Penalty event added to game '{game_id}'")

    return {"message": "Penalidade registada"}


async def add_game_event(game_id: ObjectId, event: dict) -> None:
    await db.db[GAMES_COLLECTION].update_one(
        {"_id": game_id}, {"$push": {"events": event}}
    )
