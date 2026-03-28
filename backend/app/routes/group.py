from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, GROUPS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import CreateGroupDto, GroupDto
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger

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

    get_logger().info(f"[{current_user['username']}] Creating group '{group.name}'")
    tournament = await get_tournament(group.tournament)
    group_dict = group.model_dump()
    group_dict["tournament"] = ObjectId(group.tournament)
    team_object_ids = [ObjectId(t) for t in group.teams]

    existing_groups = (
        await db.db[GROUPS_COLLECTION]
        .find(
            {
                "tournament": ObjectId(group.tournament),
                "teams": {"$in": team_object_ids},
            }
        )
        .to_list(100)
    )

    if existing_groups:
        teams_in_groups = set()
        for g in existing_groups:
            for t in g.get("teams", []):
                teams_in_groups.add(str(t))

        conflicting_teams = [t for t in group.teams if t in teams_in_groups]
        if conflicting_teams:
            raise Error.bad_request(
                "Uma ou mais equipas já pertencem a outro grupo neste torneios"
            )

    group_dict["teams"] = team_object_ids

    result = await db.db[GROUPS_COLLECTION].insert_one(group_dict)

    get_logger().info(
        f"Adding group '{group.name}' to tournament '{tournament['name']}'"
    )
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"groups": result.inserted_id}}
    )
    get_logger().info(
        f"[{current_user['username']}] Group '{group.name}' created successfully"
    )

    return group_to_dto(group_dict)


@router.get("", response_model=List[GroupDto])
async def get_groups():
    get_logger().info("Retrieving all groups")
    groups = await db.db[GROUPS_COLLECTION].find().to_list(1000)
    get_logger().info(f"Retrieved {len(groups)} groups")
    return [group_to_dto(group) for group in groups]


@router.put("/{group_id}", response_model=GroupDto)
async def update_group(
    group_id: str, group: CreateGroupDto, current_user=Depends(get_current_user)
):
    from app.routes.tournament import get_tournament

    try:
        existing_group = await db.db[GROUPS_COLLECTION].find_one(
            {"_id": ObjectId(group_id)}
        )
    except Exception:
        raise Error.invalid_id("group")
    if not existing_group:
        raise Error.not_found("Group")

    tournament = await get_tournament(group.tournament)
    team_object_ids = [ObjectId(t) for t in group.teams]

    existing_groups = (
        await db.db[GROUPS_COLLECTION]
        .find(
            {
                "tournament": ObjectId(group.tournament),
                "teams": {"$in": team_object_ids},
                "_id": {"$ne": ObjectId(group_id)},
            }
        )
        .to_list(100)
    )

    if existing_groups:
        teams_in_groups = set()
        for g in existing_groups:
            for t in g.get("teams", []):
                teams_in_groups.add(str(t))

        conflicting_teams = [t for t in group.teams if t in teams_in_groups]
        if conflicting_teams:
            raise Error.bad_request(
                "Uma ou mais equipas já pertencem a outro grupo neste torneios"
            )

    await db.db[GROUPS_COLLECTION].update_one(
        {"_id": ObjectId(group_id)},
        {"$set": {"name": group.name, "teams": team_object_ids}},
    )

    updated_group = await db.db[GROUPS_COLLECTION].find_one({"_id": ObjectId(group_id)})
    get_logger().info(
        f"[{current_user['username']}] Group '{group_id}' updated successfully"
    )

    return group_to_dto(updated_group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(group_id: str, current_user=Depends(get_current_user)):
    try:
        group = await db.db[GROUPS_COLLECTION].find_one({"_id": ObjectId(group_id)})
    except Exception:
        raise Error.invalid_id("group")
    if not group:
        raise Error.not_found("Group")

    await db.db[GROUPS_COLLECTION].delete_one({"_id": ObjectId(group_id)})
    get_logger().info(
        f"[{current_user['username']}] Group '{group_id}' deleted successfully"
    )
