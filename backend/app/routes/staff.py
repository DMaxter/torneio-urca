from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import db, STAFF_COLLECTION, TEAMS_COLLECTION
from app.schemas.schemas import StaffDto, CreateStaffDto
from app.models.models import StaffType
from app.utils.auth import get_current_user, require_manage_players
from app.utils import get_logger, sanitize_for_serialization, upload_single_file
from app.error import Error

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
async def create_staff(
    staff: CreateStaffDto, current_user=Depends(require_manage_players)
):
    get_logger().info(f"[{current_user['username']}] Creating staff '{staff.name}'")
    staff_dict = staff.model_dump()
    result = await db.db[STAFF_COLLECTION].insert_one(staff_dict)
    staff_dict["_id"] = result.inserted_id
    get_logger().info(f"Staff '{staff.name}' created successfully")
    return staff_to_dto(staff_dict)


@router.put("/{staff_id}", response_model=StaffDto)
async def update_staff(
    staff_id: str,
    name: str = Form(...),
    birth_date: str = Form(...),
    staff_type: StaffType = Form(...),
    fiscal_number: str = Form(""),
    team_id: str | None = Form(None),
    address: str = Form(""),
    place_of_birth: str = Form(""),
    citizen_card: UploadFile | None = File(None),
    current_user=Depends(require_manage_players),
):
    get_logger().info(f"[{current_user['username']}] Updating staff '{staff_id}'")
    try:
        existing = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise Error.invalid_id("staff")
    if not existing:
        raise Error.not_found("Staff")

    update_data = {
        "name": name,
        "birth_date": datetime.fromisoformat(birth_date.replace("Z", "+00:00")),
        "fiscal_number": fiscal_number,
        "staff_type": staff_type,
        "team": team_id,
    }

    if address:
        update_data["address"] = address
    if place_of_birth:
        update_data["place_of_birth"] = place_of_birth

    if citizen_card:
        file_id = await upload_single_file(
            citizen_card,
            f"staff_{staff_id}_citizen_card",
        )
        update_data["citizen_card_file_id"] = file_id

    # Get old team before updating
    old_team_id = existing.get("team")

    await db.db[STAFF_COLLECTION].update_one(
        {"_id": ObjectId(staff_id)}, {"$set": update_data}
    )

    # Staff field mappings (moved outside for reuse)
    staff_field_map = {
        StaffType.Coach: "main_coach",
        StaffType.AssistantCoach: "assistant_coach",
        StaffType.Physiotherapist: "physiotherapist",
        StaffType.GameDeputy: "first_deputy",
        "Coach": "main_coach",
        "AssistantCoach": "assistant_coach",
        "Physiotherapist": "physiotherapist",
        "GameDeputy": "first_deputy",
    }
    staff_type_labels = {
        StaffType.Coach: "Treinador Principal",
        StaffType.AssistantCoach: "Treinador Adjunto",
        StaffType.Physiotherapist: "Fisioterapeuta",
        StaffType.GameDeputy: "Delegado",
    }

    # Clear old team using OLD staff_type (in case it changed during update)
    old_staff_type = existing.get("staff_type")
    old_staff_field = staff_field_map.get(old_staff_type)

    # Clear old team if staff is moving to a different team or changing role
    if old_staff_field and old_team_id:
        if str(old_team_id) != str(team_id) or old_staff_type != staff_type:
            await db.db[TEAMS_COLLECTION].update_one(
                {"_id": ObjectId(str(old_team_id))},
                {"$set": {old_staff_field: None}},
            )

    staff_field = staff_field_map.get(staff_type)

    if team_id:
        try:
            team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
        except Exception:
            raise Error.invalid_id("team")
        if not team:
            raise Error.not_found("Team")

        if staff_field:
            existing_staff_id = team.get(staff_field)
            if existing_staff_id and str(existing_staff_id) != staff_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"A função {staff_type_labels.get(staff_type, staff_type.value)} já está atribuída nesta equipa",
                )

            await db.db[TEAMS_COLLECTION].update_one(
                {"_id": ObjectId(team_id)},
                {"$set": {staff_field: staff_id}},
            )

    updated = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
    return staff_to_dto(updated)


@router.delete("/{staff_id}", status_code=204)
async def delete_staff(staff_id: str, current_user=Depends(require_manage_players)):
    get_logger().info(f"[{current_user['username']}] Deleting staff '{staff_id}'")
    try:
        staff = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise Exception("Invalid staff ID")
    if not staff:
        raise Exception("Staff not found")

    staff_field_map = {
        StaffType.Coach: "main_coach",
        StaffType.AssistantCoach: "assistant_coach",
        StaffType.Physiotherapist: "physiotherapist",
        StaffType.GameDeputy: "first_deputy",
        "Coach": "main_coach",
        "AssistantCoach": "assistant_coach",
        "Physiotherapist": "physiotherapist",
        "GameDeputy": "first_deputy",
    }

    old_team_id = staff.get("team")
    old_staff_type = staff.get("staff_type")
    old_staff_field = staff_field_map.get(old_staff_type)

    if old_staff_field and old_team_id:
        await db.db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(str(old_team_id))},
            {"$set": {old_staff_field: None}},
        )

    await db.db[STAFF_COLLECTION].delete_one({"_id": ObjectId(staff_id)})


@router.post("/admin", response_model=StaffDto, status_code=201)
async def create_staff_admin(
    name: str = Form(...),
    birth_date: str = Form(...),
    staff_type: StaffType = Form(...),
    fiscal_number: str = Form(""),
    team_id: str = Form(...),
    tournament_id: str = Form(...),
    address: str = Form(""),
    place_of_birth: str = Form(""),
    citizen_card: UploadFile = File(...),
    current_user=Depends(require_manage_players),
):
    get_logger().info(
        f"[{current_user['username']}] Creating staff '{name}' for team '{team_id}'"
    )

    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    staff_field_map = {
        StaffType.Coach: "main_coach",
        StaffType.AssistantCoach: "assistant_coach",
        StaffType.Physiotherapist: "physiotherapist",
        StaffType.GameDeputy: "first_deputy",
    }
    staff_type_labels = {
        StaffType.Coach: "Treinador Principal",
        StaffType.AssistantCoach: "Treinador Adjunto",
        StaffType.Physiotherapist: "Fisioterapeuta",
        StaffType.GameDeputy: "Delegado",
    }
    staff_field = staff_field_map.get(staff_type)
    if staff_field:
        existing_staff_id = team.get(staff_field)
        if existing_staff_id:
            raise HTTPException(
                status_code=400,
                detail=f"A função {staff_type_labels.get(staff_type, staff_type.value)} já está atribuída nesta equipa",
            )

    player_birth_date = datetime.fromisoformat(birth_date.replace("Z", "+00:00"))

    file_dict = {}
    if citizen_card:
        file_id = await upload_single_file(
            citizen_card,
            f"admin_{team_id}_{name}_citizen_card",
        )
        file_dict["citizen_card_file_id"] = file_id

    staff_dict = {
        "name": name,
        "birth_date": player_birth_date,
        "address": address,
        "place_of_birth": place_of_birth,
        "fiscal_number": fiscal_number,
        "staff_type": staff_type,
        "team": team_id,
        **file_dict,
    }
    result = await db.db[STAFF_COLLECTION].insert_one(staff_dict)
    staff_dict["_id"] = result.inserted_id

    staff_field_map = {
        StaffType.Coach: "main_coach",
        StaffType.AssistantCoach: "assistant_coach",
        StaffType.Physiotherapist: "physiotherapist",
        StaffType.GameDeputy: "first_deputy",
    }
    staff_field = staff_field_map.get(staff_type)
    if staff_field:
        await db.db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$set": {staff_field: str(result.inserted_id)}},
        )

    get_logger().info(f"Staff '{name}' created and added to team successfully")
    return staff_to_dto(staff_dict)
