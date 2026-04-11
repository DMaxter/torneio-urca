from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, STAFF_COLLECTION, TEAMS_COLLECTION
from app.schemas.schemas import StaffDto, CreateStaffDto
from app.models.models import StaffType
from app.utils.auth import get_current_user
from app.utils import get_logger, sanitize_for_serialization

router = APIRouter(prefix="/staff", tags=["Staff"])

FIELD_TO_STAFF_TYPE = {
    "Coach": StaffType.Coach,
    "AssistantCoach": StaffType.AssistantCoach,
    "Physiotherapist": StaffType.Physiotherapist,
    "GameDeputy": StaffType.GameDeputy,
}


def staff_to_dto(staff: dict) -> StaffDto:
    clean = sanitize_for_serialization(staff)
    raw_staff_type = clean.get("staff_type", "")
    staff_type_enum = FIELD_TO_STAFF_TYPE.get(raw_staff_type, StaffType.GameDeputy)
    return StaffDto(
        id=clean["_id"],
        name=clean["name"],
        birth_date=clean["birth_date"],
        address=clean.get("address"),
        place_of_birth=clean.get("place_of_birth"),
        fiscal_number=clean["fiscal_number"],
        staff_type=staff_type_enum,
        citizen_card_file_id=clean.get("citizen_card_file_id"),
        proof_of_residency_file_id=clean.get("proof_of_residency_file_id"),
        authorization_file_id=clean.get("authorization_file_id"),
    )


@router.get("", response_model=List[StaffDto])
async def get_all_staff():
    get_logger().info("Retrieving all staff")
    staff_list = await db.db[STAFF_COLLECTION].find().to_list(1000)

    teams = (
        await db.db[TEAMS_COLLECTION]
        .find(
            {
                "$or": [
                    {"main_coach": {"$ne": None}},
                    {"assistant_coach": {"$ne": None}},
                    {"physiotherapist": {"$ne": None}},
                    {"first_deputy": {"$ne": None}},
                    {"second_deputy": {"$ne": None}},
                ]
            }
        )
        .to_list(1000)
    )

    staff_id_to_team = {}
    for team in teams:
        for field in [
            "main_coach",
            "assistant_coach",
            "physiotherapist",
            "first_deputy",
            "second_deputy",
        ]:
            staff_id = team.get(field)
            if staff_id:
                staff_id_to_team[str(staff_id)] = team.get("name", "")

    result = []
    for staff in staff_list:
        staff_dto = staff_to_dto(staff)
        staff_dict = staff_dto.model_dump()
        staff_dict["team_name"] = staff_id_to_team.get(str(staff["_id"]), None)
        result.append(StaffDto(**staff_dict))

    return result


@router.post("", response_model=StaffDto, status_code=201)
async def create_staff(staff: CreateStaffDto, current_user=Depends(get_current_user)):
    get_logger().info(f"[{current_user['username']}] Creating staff '{staff.name}'")
    staff_dict = staff.model_dump()
    result = await db.db[STAFF_COLLECTION].insert_one(staff_dict)
    staff_dict["_id"] = result.inserted_id
    return staff_to_dto(staff_dict)


@router.put("/{staff_id}", response_model=StaffDto)
async def update_staff(
    staff_id: str, staff: CreateStaffDto, current_user=Depends(get_current_user)
):
    get_logger().info(f"[{current_user['username']}] Updating staff '{staff_id}'")
    try:
        existing = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise Error.invalid_id("staff")
    if not existing:
        raise Error.not_found("Staff")

    update_data = {
        "name": staff.name,
        "birth_date": staff.birth_date,
        "fiscal_number": staff.fiscal_number,
    }

    await db.db[STAFF_COLLECTION].update_one(
        {"_id": ObjectId(staff_id)}, {"$set": update_data}
    )

    updated = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
    return staff_to_dto(updated)


@router.delete("/{staff_id}", status_code=204)
async def delete_staff(staff_id: str, current_user=Depends(get_current_user)):
    get_logger().info(f"[{current_user['username']}] Deleting staff '{staff_id}'")
    try:
        staff = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise Exception("Invalid staff ID")
    if not staff:
        raise Exception("Staff not found")
    await db.db[STAFF_COLLECTION].delete_one({"_id": ObjectId(staff_id)})
