import secrets
from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel

from database import (
    db,
    TEAM_COUNTS_COLLECTION,
    VOTE_HISTORY_COLLECTION,
    SETTINGS_COLLECTION,
)
from app.utils.auth import get_admin_user
from app.utils import get_logger

router = APIRouter(prefix="/pinga", tags=["Taca da Pinga"])

API_KEY_SETTING = "taca_da_pinga_api_key"


class VoteRequest(BaseModel):
    team_name: str
    count: int = 1


class TeamCount(BaseModel):
    team_name: str
    count: int


class DailyVoteHistory(BaseModel):
    date: str
    teams: List[TeamCount]


def _get_api_key() -> str:
    return API_KEY_SETTING


def _get_or_create_api_key() -> str:
    key = API_KEY_SETTING
    return key


async def _ensure_api_key():
    doc = await db.db[SETTINGS_COLLECTION].find_one({"key": API_KEY_SETTING})
    if not doc:
        new_key = secrets.token_urlsafe(32)
        await db.db[SETTINGS_COLLECTION].insert_one(
            {
                "key": API_KEY_SETTING,
                "value": new_key,
                "created_at": datetime.now(timezone.utc),
            }
        )


async def _get_current_api_key() -> Optional[str]:
    doc = await db.db[SETTINGS_COLLECTION].find_one({"key": API_KEY_SETTING})
    if doc:
        return doc.get("value")
    return None


def _verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    return x_api_key


@router.post("/vote")
async def vote(data: VoteRequest, api_key: Optional[str] = Depends(_verify_api_key)):
    await _ensure_api_key()

    current_key = await _get_current_api_key()
    if not current_key or not api_key or api_key != current_key:
        raise HTTPException(status_code=401, detail="Chave API inválida")

    if data.count <= 0:
        raise HTTPException(status_code=400, detail="Contagem deve ser maior que 0")

    timestamp = datetime.now(timezone.utc)
    date_string = timestamp.strftime("%Y-%m-%d")

    await db.db[TEAM_COUNTS_COLLECTION].update_one(
        {"team_name": data.team_name},
        {"$inc": {"count": data.count}, "$set": {"updated_at": timestamp}},
        upsert=True,
    )

    await db.db[VOTE_HISTORY_COLLECTION].update_one(
        {"team_name": data.team_name, "date": date_string},
        {"$inc": {"count": data.count}},
        upsert=True,
    )

    return {"success": True, "team_name": data.team_name, "count": data.count}


@router.get("/counts", response_model=List[TeamCount])
async def get_counts():
    cursor = db.db[TEAM_COUNTS_COLLECTION].find()
    counts = []
    async for doc in cursor:
        counts.append(TeamCount(team_name=doc["team_name"], count=doc.get("count", 0)))
    return sorted(counts, key=lambda x: x.count, reverse=True)


@router.get("/history", response_model=List[DailyVoteHistory])
async def get_history():
    cursor = db.db[VOTE_HISTORY_COLLECTION].find()
    docs = []
    async for doc in cursor:
        docs.append(
            {
                "date": doc["date"],
                "team_name": doc["team_name"],
                "count": doc.get("count", 0),
            }
        )

    by_date = {}
    for d in docs:
        date = d["date"]
        if date not in by_date:
            by_date[date] = {"date": date, "teams": []}
        by_date[date]["teams"].append(
            TeamCount(team_name=d["team_name"], count=d["count"])
        )

    for date_data in by_date.values():
        date_data["teams"] = sorted(
            date_data["teams"], key=lambda x: x.count, reverse=True
        )

    return sorted(by_date.values(), key=lambda x: x["date"])


@router.get("/api-key")
async def get_api_key(current_user=Depends(get_admin_user)):
    await _ensure_api_key()
    key = await _get_current_api_key()
    return {"api_key": key}


@router.post("/api-key/rotate")
async def rotate_api_key(current_user=Depends(get_admin_user)):
    new_key = secrets.token_urlsafe(32)
    await db.db[SETTINGS_COLLECTION].update_one(
        {"key": API_KEY_SETTING},
        {
            "$set": {
                "value": new_key,
                "rotated_at": datetime.now(timezone.utc),
                "rotated_by": current_user["username"],
            }
        },
        upsert=True,
    )
    get_logger().info(f"[{current_user['username']}] Rotated Taça da Pinga API key")
    return {"api_key": new_key}
