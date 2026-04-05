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
)
from app.models.models import GameStatus, GamePhase
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger

router = APIRouter(prefix="/games", tags=["Games"])


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


def game_to_dto(game: dict, home_call: dict | None, away_call: dict | None) -> GameDto:
    return GameDto(
        id=str(game["_id"]),
        tournament=str(game["tournament"]),
        scheduled_date=game.get("scheduled_date"),
        start_date=game.get("start_date"),
        finish_date=game.get("finish_date"),
        status=game.get("status", GameStatus.NotStarted),
        phase=game.get("phase", GamePhase.Group),
        home_placeholder=game.get("home_placeholder"),
        away_placeholder=game.get("away_placeholder"),
        home_call=game_call_to_dto(home_call) if home_call else None,
        away_call=game_call_to_dto(away_call) if away_call else None,
        events=game.get("events", []),
    )


@router.post("", response_model=GameDto, status_code=201)
async def add_game(game: CreateGameDto, current_user=Depends(get_current_user)):
    from app.routes.tournament import get_tournament

    get_logger().info(
        f"[{current_user['username']}] Creating game for tournament '{game.tournament}'"
    )
    tournament = await get_tournament(game.tournament)

    game_dict = {
        "tournament": ObjectId(game.tournament),
        "scheduled_date": game.scheduled_date,
        "status": GameStatus.NotStarted,
        "phase": game.phase,
        "home_placeholder": game.home_placeholder,
        "away_placeholder": game.away_placeholder,
        "current_period": 0,
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


@router.patch("/{game_id}", response_model=GameDto)
async def update_game(
    game_id: str, body: UpdateGameDto, current_user=Depends(get_current_user)
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
async def delete_game(game_id: str, current_user=Depends(get_current_user)):
    game = await get_game(game_id)
    await db.db[GAME_CALLS_COLLECTION].delete_many(
        {"_id": {"$in": [game.get("home_call"), game.get("away_call")]}}
    )
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": game["tournament"]}, {"$pull": {"games": game["_id"]}}
    )
    await db.db[GAMES_COLLECTION].delete_one({"_id": game["_id"]})
    get_logger().info(f"[{current_user['username']}] Deleted game '{game_id}'")


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
