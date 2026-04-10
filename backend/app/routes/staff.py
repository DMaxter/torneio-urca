from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, STAFF_COLLECTION, TEAMS_COLLECTION
from app.schemas.schemas import StaffDto, CreateStaffDto
from app.models.models import StaffType
from app.utils.auth import get_current_user
from app.utils import get_logger, sanitize_for_serialization

router = APIRouter(prefix="/staff", tags=["Staff"])

STAFF_TYPE_TO_FIELD = {
    StaffType.Coach: "main_coach",
    StaffType.AssistantCoach: "assistant_coach",
    StaffType.Physiotherapist: "physiotherapist",
    StaffType.GameDeputy: "first_deputy",
}


def staff_to_dto(staff: dict) -> StaffDto:
    clean = sanitize_for_serialization(staff)
    raw_staff_type = clean.get("staff_type", "")
    field_name = STAFF_TYPE_TO_FIELD.get(raw_staff_type, raw_staff_type)
    return StaffDto(
        id=clean["_id"],
        name=clean["name"],
        birth_date=clean["birth_date"],
        address=clean.get("address"),
        place_of_birth=clean.get("place_of_birth"),
        fiscal_number=clean["fiscal_number"],
        staff_type=field_name,
        citizen_card_file_id=clean.get("citizen_card_file_id"),
        proof_of_residency_file_id=clean.get("proof_of_residency_file_id"),
        authorization_file_id=clean.get("authorization_file_id"),
    )


@router.get("", response_model=List[StaffDto])
async def get_all_staff():
    get_logger().info("Retrieving all staff")
    staff_list = await db.db[STAFF_COLLECTION].find().to_list(1000)
    return [staff_to_dto(s) for s in staff_list]


@router.post("", response_model=StaffDto, status_code=201)
async def create_staff(staff: CreateStaffDto, current_user=Depends(get_current_user)):
    get_logger().info(f"[{current_user['username']}] Creating staff '{staff.name}'")
    staff_dict = staff.model_dump()
    result = await db.db[STAFF_COLLECTION].insert_one(staff_dict)
    staff_dict["_id"] = result.inserted_id
    return staff_to_dto(staff_dict)


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
