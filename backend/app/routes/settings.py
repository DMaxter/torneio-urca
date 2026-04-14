from fastapi import APIRouter, Depends
from database import db, SETTINGS_COLLECTION
from app.utils.auth import require_open_calendar
from app.utils import get_logger

router = APIRouter(prefix="/settings", tags=["Settings"])

SINGLETON_KEY = "global"


async def _get_doc() -> dict:
    doc = await db.db[SETTINGS_COLLECTION].find_one({"key": SINGLETON_KEY})
    return doc or {"key": SINGLETON_KEY, "calendar_locked": False}


@router.get("")
async def get_settings():
    doc = await _get_doc()
    return {"calendar_locked": doc.get("calendar_locked", False)}


@router.patch("/calendar-lock")
async def toggle_calendar_lock(current_user=Depends(require_open_calendar)):
    doc = await _get_doc()
    new_value = not doc.get("calendar_locked", False)
    await db.db[SETTINGS_COLLECTION].update_one(
        {"key": SINGLETON_KEY},
        {"$set": {"calendar_locked": new_value}},
        upsert=True,
    )
    get_logger().info(f"[{current_user['username']}] calendar_locked → {new_value}")
    return {"calendar_locked": new_value}
