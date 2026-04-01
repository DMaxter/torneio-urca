from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends

from database import db, GAME_DAYS_COLLECTION
from app.schemas.schemas import CreateGameDayDto, GameDayDto
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger

router = APIRouter(prefix="/game-days", tags=["GameDays"])


def game_day_to_dto(day: dict) -> GameDayDto:
    return GameDayDto(
        id=str(day["_id"]),
        tournament=str(day["tournament"]),
        date=day["date"],
        num_games=day["num_games"],
        start_time=day["start_time"],
    )


@router.get("", response_model=List[GameDayDto])
async def get_game_days():
    days = await db.db[GAME_DAYS_COLLECTION].find().to_list(1000)
    return [game_day_to_dto(d) for d in days]


@router.post("", response_model=GameDayDto, status_code=201)
async def create_game_day(day: CreateGameDayDto, current_user=Depends(get_current_user)):
    get_logger().info(f"[{current_user['username']}] Creating game day for tournament '{day.tournament}'")
    doc = {
        "tournament": ObjectId(day.tournament),
        "date": day.date,
        "num_games": day.num_games,
        "start_time": day.start_time,
    }
    result = await db.db[GAME_DAYS_COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return game_day_to_dto(doc)


@router.delete("/{day_id}", status_code=204)
async def delete_game_day(day_id: str, current_user=Depends(get_current_user)):
    try:
        oid = ObjectId(day_id)
    except Exception:
        raise Error.invalid_id("game day")
    result = await db.db[GAME_DAYS_COLLECTION].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise Error.not_found("GameDay")
    get_logger().info(f"[{current_user['username']}] Deleted game day '{day_id}'")
