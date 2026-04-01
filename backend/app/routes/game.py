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
from app.schemas.schemas import CreateGameDto, GameDto, GameCallDto
from app.models.models import GameStatus
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger

router = APIRouter(prefix="/games", tags=["Games"])


def game_call_to_dto(call: dict) -> GameCallDto:
    return GameCallDto(
        id=str(call["_id"]),
        game=str(call.get("game", "")),
        team=str(call["team"]),
        players=[str(p) for p in call.get("players", [])],
        deputy=str(call["deputy"]) if call.get("deputy") else None,
    )


def game_to_dto(game: dict, home_call: dict, away_call: dict) -> GameDto:
    return GameDto(
        id=str(game["_id"]),
        tournament=str(game["tournament"]),
        scheduled_date=game.get("scheduled_date"),
        start_date=game.get("start_date"),
        finish_date=game.get("finish_date"),
        status=game.get("status", GameStatus.NotStarted),
        home_call=game_call_to_dto(home_call),
        away_call=game_call_to_dto(away_call),
        events=game.get("events", []),
    )


@router.post("", response_model=GameDto, status_code=201)
async def add_game(game: CreateGameDto, current_user=Depends(get_current_user)):
    from app.routes.tournament import get_tournament

    get_logger().info(
        f"[{current_user['username']}] Creating game for tournament '{game.tournament}'"
    )
    tournament = await get_tournament(game.tournament)

    home_call_dict = {
        "team": ObjectId(game.home_call.team),
        "players": [],
        "deputy": None,
    }
    away_call_dict = {
        "team": ObjectId(game.away_call.team),
        "players": [],
        "deputy": None,
    }

    get_logger().info("Creating game calls for home and away teams")
    home_result = await db.db[GAME_CALLS_COLLECTION].insert_one(home_call_dict)
    away_result = await db.db[GAME_CALLS_COLLECTION].insert_one(away_call_dict)

    game_dict = {
        "tournament": ObjectId(game.tournament),
        "scheduled_date": game.scheduled_date,
        "status": GameStatus.NotStarted,
        "home_call": home_result.inserted_id,
        "away_call": away_result.inserted_id,
        "current_period": 0,
        "events": [],
    }

    result = await db.db[GAMES_COLLECTION].insert_one(game_dict)

    get_logger().info("Linking game calls to game")
    await db.db[GAME_CALLS_COLLECTION].update_many(
        {"_id": {"$in": [home_result.inserted_id, away_result.inserted_id]}},
        {"$set": {"game": result.inserted_id}},
    )

    get_logger().info(f"Adding game to tournament '{tournament['name']}'")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"games": result.inserted_id}}
    )

    home_call_dict["_id"] = home_result.inserted_id
    away_call_dict["_id"] = away_result.inserted_id
    home_call_dict["game"] = result.inserted_id
    away_call_dict["game"] = result.inserted_id

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
        home_call = calls_map.get(str(game.get("home_call")))
        away_call = calls_map.get(str(game.get("away_call")))
        if home_call and away_call:
            result.append(game_to_dto(game, home_call, away_call))

    get_logger().info(f"Retrieved {len(result)} games")
    return result


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
