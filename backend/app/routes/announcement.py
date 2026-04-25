from typing import List
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from database import db, ANNOUNCEMENTS_COLLECTION
from app.schemas.schemas import (
    CreateAnnouncementDto,
    UpdateAnnouncementDto,
    AnnouncementDto,
)
from app.utils.auth import get_current_user, require_announcer
from app.utils import get_logger, sanitize_for_serialization

router = APIRouter(prefix="/announcements", tags=["Announcements"])


def announcement_to_dto(announcement: dict) -> AnnouncementDto:
    clean = sanitize_for_serialization(announcement)
    return AnnouncementDto(
        id=clean["_id"],
        title=clean["title"],
        content=clean["content"],
        is_active=clean.get("is_active", True),
        created_at=clean["created_at"],
        updated_at=clean["updated_at"],
    )


@router.get("", response_model=List[AnnouncementDto])
async def get_announcements():
    """
    Get all announcements, ordered by creation date (newest first).
    """
    cursor = db.db[ANNOUNCEMENTS_COLLECTION].find().sort("created_at", -1)
    announcements = await cursor.to_list(length=100)
    return [announcement_to_dto(a) for a in announcements]


@router.post("", response_model=AnnouncementDto, status_code=201)
async def create_announcement(
    announcement: CreateAnnouncementDto, current_user=Depends(require_announcer)
):
    """
    Create a new announcement. Requires announcer role.
    """
    get_logger().info(
        f"[{current_user['username']}] Creating announcement '{announcement.title}'"
    )
    now = datetime.now()
    announcement_dict = {
        "title": announcement.title,
        "content": announcement.content,
        "is_active": announcement.is_active,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.db[ANNOUNCEMENTS_COLLECTION].insert_one(announcement_dict)
    announcement_dict["_id"] = result.inserted_id
    get_logger().info(
        f"[{current_user['username']}] Created announcement '{announcement.title}'"
    )
    return announcement_to_dto(announcement_dict)


@router.put("/{announcement_id}", response_model=AnnouncementDto)
async def update_announcement(
    announcement_id: str,
    announcement: UpdateAnnouncementDto,
    current_user=Depends(require_announcer),
):
    """
    Update an announcement. Requires announcer role.
    """
    existing = await db.db[ANNOUNCEMENTS_COLLECTION].find_one(
        {"_id": ObjectId(announcement_id)}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")

    get_logger().info(
        f"[{current_user['username']}] Updating announcement '{announcement_id}'"
    )

    update_data = {k: v for k, v in announcement.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now()

    await db.db[ANNOUNCEMENTS_COLLECTION].update_one(
        {"_id": ObjectId(announcement_id)},
        {"$set": update_data},
    )

    updated = await db.db[ANNOUNCEMENTS_COLLECTION].find_one(
        {"_id": ObjectId(announcement_id)}
    )
    get_logger().info(
        f"[{current_user['username']}] Updated announcement '{announcement_id}'"
    )
    return announcement_to_dto(updated)


@router.delete("/{announcement_id}", status_code=204)
async def delete_announcement(
    announcement_id: str, current_user=Depends(require_announcer)
):
    """
    Delete an announcement. Requires announcer role.
    """
    existing = await db.db[ANNOUNCEMENTS_COLLECTION].find_one(
        {"_id": ObjectId(announcement_id)}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")

    get_logger().info(
        f"[{current_user['username']}] Deleting announcement '{announcement_id}'"
    )
    await db.db[ANNOUNCEMENTS_COLLECTION].delete_one({"_id": ObjectId(announcement_id)})
    get_logger().info(
        f"[{current_user['username']}] Deleted announcement '{announcement_id}'"
    )
