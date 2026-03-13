from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from database import (
    db,
    TEAMS_COLLECTION,
    TOURNAMENTS_COLLECTION,
    PLAYERS_COLLECTION,
    STAFF_COLLECTION,
)
from app.schemas.schemas import CreateTeamDto, TeamDto, StaffType
from app.error import Error
from datetime import datetime, timezone
import json

router = APIRouter(prefix="/teams", tags=["Teams"])


def team_to_dto(team: dict) -> TeamDto:
    return TeamDto(
        id=str(team["_id"]),
        tournament=str(team["tournament"]),
        name=team["name"],
        responsible_name=team["responsible_name"],
        responsible_email=team["responsible_email"],
        responsible_phone=team["responsible_phone"],
        main_coach=str(team["main_coach"]),
        assistant_coach=str(team["assistant_coach"])
        if team.get("assistant_coach")
        else None,
        players=[str(p) for p in team.get("players", [])],
        physiotherapist=str(team["physiotherapist"]),
        first_deputy=str(team["first_deputy"]),
        second_deputy=str(team["second_deputy"]) if team.get("second_deputy") else None,
    )


@router.post("", response_model=TeamDto, status_code=201)
async def add_team(team: CreateTeamDto):
    from app.routes.tournament import get_tournament

    tournament = await get_tournament(team.tournament)
    team_dict = team.model_dump()
    team_dict["tournament"] = ObjectId(team.tournament)
    team_dict["main_coach"] = ObjectId(team.main_coach)
    team_dict["assistant_coach"] = (
        ObjectId(team.assistant_coach) if team.assistant_coach else None
    )
    team_dict["players"] = [ObjectId(p) for p in team.players]
    team_dict["physiotherapist"] = ObjectId(team.physiotherapist)
    team_dict["first_deputy"] = ObjectId(team.first_deputy)
    team_dict["second_deputy"] = (
        ObjectId(team.second_deputy) if team.second_deputy else None
    )
    team_dict["valid"] = False

    result = await db.db[TEAMS_COLLECTION].insert_one(team_dict)

    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"teams": result.inserted_id}}
    )

    return team_to_dto(team_dict)


@router.post("/register", response_model=TeamDto, status_code=201)
async def register_team(
    tournament: str = Form(...),
    name: str = Form(...),
    responsible_name: str = Form(...),
    responsible_email: str = Form(...),
    responsible_phone: str = Form(...),
    main_coach_name: Optional[str] = Form(None),
    main_coach_birth_date: Optional[str] = Form(None),
    main_coach_address: Optional[str] = Form(None),
    main_coach_place_of_birth: Optional[str] = Form(None),
    main_coach_fiscal_number: Optional[str] = Form(None),
    physiotherapist_name: Optional[str] = Form(None),
    physiotherapist_birth_date: Optional[str] = Form(None),
    physiotherapist_address: Optional[str] = Form(None),
    physiotherapist_place_of_birth: Optional[str] = Form(None),
    physiotherapist_fiscal_number: Optional[str] = Form(None),
    first_deputy_name: Optional[str] = Form(None),
    first_deputy_birth_date: Optional[str] = Form(None),
    first_deputy_address: Optional[str] = Form(None),
    first_deputy_place_of_birth: Optional[str] = Form(None),
    first_deputy_fiscal_number: Optional[str] = Form(None),
    second_deputy_name: Optional[str] = Form(None),
    second_deputy_birth_date: Optional[str] = Form(None),
    second_deputy_address: Optional[str] = Form(None),
    second_deputy_place_of_birth: Optional[str] = Form(None),
    second_deputy_fiscal_number: Optional[str] = Form(None),
    players_json: str = Form(...),
    files: List[UploadFile] = File(...),
):
    from app.routes.tournament import get_tournament

    players = json.loads(players_json)
    if len(players) < 5:
        raise HTTPException(
            status_code=400, detail="É necessário um mínimo de 5 jogadores"
        )

    await get_tournament(tournament)

    file_dict = {}
    for f in files:
        content = await f.read()
        filename = f.filename or "unknown"
        content_type = f.content_type or "application/octet-stream"
        file_id = await db.upload_file(filename, content_type, content)
        file_dict[filename] = file_id

    main_coach_id = None
    if main_coach_name:
        main_coach_data = {
            "name": main_coach_name,
            "birth_date": datetime.fromisoformat(main_coach_birth_date)
            if main_coach_birth_date
            else None,
            "address": main_coach_address,
            "place_of_birth": main_coach_place_of_birth,
            "fiscal_number": main_coach_fiscal_number,
            "staff_type": StaffType.Coach,
            "citizen_card_file_id": file_dict.get("main_coach_citizen_card"),
            "proof_of_residency_file_id": file_dict.get(
                "main_coach_proof_of_residency"
            ),
        }
        main_coach_result = await db.db[STAFF_COLLECTION].insert_one(main_coach_data)
        main_coach_id = main_coach_result.inserted_id

    physiotherapist_id = None
    if physiotherapist_name:
        physiotherapist_data = {
            "name": physiotherapist_name,
            "birth_date": datetime.fromisoformat(physiotherapist_birth_date)
            if physiotherapist_birth_date
            else None,
            "address": physiotherapist_address,
            "place_of_birth": physiotherapist_place_of_birth,
            "fiscal_number": physiotherapist_fiscal_number,
            "staff_type": StaffType.Physiotherapist,
            "citizen_card_file_id": file_dict.get("physiotherapist_citizen_card"),
            "proof_of_residency_file_id": file_dict.get(
                "physiotherapist_proof_of_residency"
            ),
        }
        physio_result = await db.db[STAFF_COLLECTION].insert_one(physiotherapist_data)
        physiotherapist_id = physio_result.inserted_id

    first_deputy_id = None
    if first_deputy_name:
        first_deputy_data = {
            "name": first_deputy_name,
            "birth_date": datetime.fromisoformat(first_deputy_birth_date)
            if first_deputy_birth_date
            else None,
            "address": first_deputy_address,
            "place_of_birth": first_deputy_place_of_birth,
            "fiscal_number": first_deputy_fiscal_number,
            "staff_type": StaffType.GameDeputy,
            "citizen_card_file_id": file_dict.get("first_deputy_citizen_card"),
            "proof_of_residency_file_id": file_dict.get(
                "first_deputy_proof_of_residency"
            ),
        }
        first_deputy_result = await db.db[STAFF_COLLECTION].insert_one(
            first_deputy_data
        )
        first_deputy_id = first_deputy_result.inserted_id

    second_deputy_id = None
    if second_deputy_name and second_deputy_fiscal_number and second_deputy_birth_date:
        second_deputy_data = {
            "name": second_deputy_name,
            "birth_date": datetime.fromisoformat(second_deputy_birth_date),
            "address": second_deputy_address,
            "place_of_birth": second_deputy_place_of_birth,
            "fiscal_number": second_deputy_fiscal_number,
            "staff_type": StaffType.GameDeputy,
            "citizen_card_file_id": file_dict.get("second_deputy_citizen_card"),
            "proof_of_residency_file_id": file_dict.get(
                "second_deputy_proof_of_residency"
            ),
        }
        second_deputy_result = await db.db[STAFF_COLLECTION].insert_one(
            second_deputy_data
        )
        second_deputy_id = second_deputy_result.inserted_id

    player_ids = []
    for i, player in enumerate(players):
        player_birth_date = datetime.fromisoformat(
            player["birth_date"].replace("Z", "+00:00")
        )
        age = (
            datetime.now(timezone.utc) - player_birth_date.replace(tzinfo=timezone.utc)
        ).days // 365

        if age < 16 and f"player_{i}_authorization" not in file_dict:
            raise HTTPException(
                status_code=400,
                detail=f"O jogador {player['name']} é menor de 16 anos e requer autorização",
            )

        player_data = {
            "name": player["name"],
            "birth_date": player_birth_date,
            "address": player.get("address"),
            "place_of_birth": player.get("place_of_birth"),
            "fiscal_number": player["fiscal_number"],
            "citizen_card_file_id": file_dict.get(f"player_{i}_citizen_card"),
            "proof_of_residency_file_id": file_dict.get(
                f"player_{i}_proof_of_residency"
            ),
            "authorization_file_id": file_dict.get(f"player_{i}_authorization"),
            "is_federated": player.get("is_federated", False),
            "federation_team": player.get("federation_team"),
            "federation_exams_up_to_date": player.get(
                "federation_exams_up_to_date", False
            ),
            "is_confirmed": False,
        }
        player_result = await db.db[PLAYERS_COLLECTION].insert_one(player_data)
        player_ids.append(player_result.inserted_id)

    team_data = {
        "tournament": ObjectId(tournament),
        "name": name,
        "responsible_name": responsible_name,
        "responsible_email": responsible_email,
        "responsible_phone": responsible_phone,
        "main_coach": main_coach_id,
        "physiotherapist": physiotherapist_id,
        "first_deputy": first_deputy_id,
        "second_deputy": second_deputy_id,
        "players": player_ids,
        "valid": False,
    }

    result = await db.db[TEAMS_COLLECTION].insert_one(team_data)
    team_data["_id"] = result.inserted_id

    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": ObjectId(tournament)}, {"$push": {"teams": result.inserted_id}}
    )

    return team_to_dto(team_data)


@router.get("", response_model=List[TeamDto])
async def get_teams():
    teams = await db.db[TEAMS_COLLECTION].find().to_list(1000)
    return [team_to_dto(team) for team in teams]


async def get_team(team_id: str) -> dict:
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")
    return team
