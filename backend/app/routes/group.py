import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, GROUPS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import CreateGroupDto, GroupDto
from app.error import Error
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/groups", tags=["Groups"])


def group_to_dto(group: dict) -> GroupDto:
    return GroupDto(
        id=str(group["_id"]),
        tournament=str(group["tournament"]),
        name=group["name"],
        teams=[str(t) for t in group.get("teams", [])],
    )


@router.post("", response_model=GroupDto, status_code=201)
async def add_group(group: CreateGroupDto, current_user=Depends(get_current_user)):
    from app.routes.tournament import get_tournament

    logger.info(f"[{current_user['username']}] Creating group: {group.name}")
    tournament = await get_tournament(group.tournament)
    group_dict = group.model_dump()
    group_dict["tournament"] = ObjectId(group.tournament)
    group_dict["teams"] = [ObjectId(t) for t in group.teams]

    result = await db.db[GROUPS_COLLECTION].insert_one(group_dict)

    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"groups": result.inserted_id}}
    )
    logger.info(f"Group created: {group.name} (id: {result.inserted_id})")

    return group_to_dto(group_dict)


@router.get("", response_model=List[GroupDto])
async def get_groups():
    groups = await db.db[GROUPS_COLLECTION].find().to_list(1000)
    logger.info(f"Retrieved {len(groups)} groups")
    return [group_to_dto(group) for group in groups]
