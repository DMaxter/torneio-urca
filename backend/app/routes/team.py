import logging
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Depends
from database import (
    db,
    TEAMS_COLLECTION,
    TOURNAMENTS_COLLECTION,
    PLAYERS_COLLECTION,
    STAFF_COLLECTION,
)
from app.schemas.schemas import CreateTeamDto, TeamDto, StaffType
from app.error import Error
from app.constants import MIN_PLAYERS, MIN_AGE
from app.utils import calculate_age
from app.utils.auth import get_current_user
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/teams", tags=["Teams"])


def team_to_dto(team: dict) -> TeamDto:
    """Convert a team document from the database to a TeamDto."""
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


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object."""
    return datetime.fromisoformat(date_str) if date_str else None


async def process_files(files: List[UploadFile]) -> dict[str, str]:
    """Upload files and return a mapping of filename to file ID."""
    file_dict = {}
    for f in files:
        content = await f.read()
        filename = f.filename or "unknown"
        content_type = f.content_type or "application/octet-stream"
        file_id = await db.upload_file(filename, content_type, content)
        file_dict[filename] = file_id
    return file_dict


def create_staff_member(
    staff_type: StaffType,
    name: Optional[str],
    birth_date: Optional[str],
    address: Optional[str],
    place_of_birth: Optional[str],
    fiscal_number: Optional[str],
    file_dict: dict[str, str],
    prefix: str,
) -> Optional[ObjectId]:
    """Create a staff member in the database if name is provided."""
    if not name:
        return None

    staff_data = {
        "name": name,
        "birth_date": parse_date(birth_date),
        "address": address,
        "place_of_birth": place_of_birth,
        "fiscal_number": fiscal_number,
        "staff_type": staff_type,
        "citizen_card_file_id": file_dict.get(f"{prefix}_citizen_card"),
        "proof_of_residency_file_id": file_dict.get(f"{prefix}_proof_of_residency"),
    }
    result = db.db[STAFF_COLLECTION].insert_one(staff_data)
    return result.inserted_id


def create_players(players: list, file_dict: dict[str, str]) -> list[ObjectId]:
    """Create players in the database and return their IDs."""
    player_ids = []
    for i, player in enumerate(players):
        player_birth_date = datetime.fromisoformat(
            player["birth_date"].replace("Z", "+00:00")
        )
        age = calculate_age(player_birth_date)

        if age < MIN_AGE and f"player_{i}_authorization" not in file_dict:
            raise HTTPException(
                status_code=400,
                detail=f"O jogador {player['name']} é menor de {MIN_AGE} anos e requer autorização",
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
        result = db.db[PLAYERS_COLLECTION].insert_one(player_data)
        player_ids.append(result.inserted_id)
    return player_ids


@router.post("", response_model=TeamDto, status_code=201)
async def add_team(team: CreateTeamDto, current_user=Depends(get_current_user)):
    """Create a new team by providing full references to existing entities."""
    from app.routes.tournament import get_tournament

    logger.info(f"[{current_user['username']}] Creating team: {team.name}")
    tournament = await get_tournament(team.tournament)
    team_dict = team.model_dump()
    team_dict["tournament"] = ObjectId(team.tournament)
    team_dict["main_coach"] = ObjectId(team.main_coach) if team.main_coach else None
    team_dict["assistant_coach"] = (
        ObjectId(team.assistant_coach) if team.assistant_coach else None
    )
    team_dict["players"] = [ObjectId(p) for p in team.players] if team.players else []
    team_dict["physiotherapist"] = (
        ObjectId(team.physiotherapist) if team.physiotherapist else None
    )
    team_dict["first_deputy"] = (
        ObjectId(team.first_deputy) if team.first_deputy else None
    )
    team_dict["second_deputy"] = (
        ObjectId(team.second_deputy) if team.second_deputy else None
    )
    team_dict["valid"] = False

    result = await db.db[TEAMS_COLLECTION].insert_one(team_dict)

    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"teams": result.inserted_id}}
    )
    logger.info(f"Team created: {team.name} (id: {result.inserted_id})")
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
    """
    Register a new team with all associated staff and players.

    This endpoint handles the full team registration workflow including:
    - Validating minimum player count
    - Processing uploaded files (citizen cards, proof of residency, authorizations)
    - Creating staff members (coach, physiotherapist, deputies)
    - Creating player records with age validation (authorization required for minors)
    - Associating the team with the specified tournament
    """
    from app.routes.tournament import get_tournament

    logger.info(f"Team registration request: {name}")
    players = json.loads(players_json)
    if len(players) < MIN_PLAYERS:
        raise HTTPException(
            status_code=400, detail=f"É necessário um mínimo de {MIN_PLAYERS} jogadores"
        )

    await get_tournament(tournament)
    file_dict = await process_files(files)

    main_coach_id = create_staff_member(
        StaffType.Coach,
        main_coach_name,
        main_coach_birth_date,
        main_coach_address,
        main_coach_place_of_birth,
        main_coach_fiscal_number,
        file_dict,
        "main_coach",
    )
    physiotherapist_id = create_staff_member(
        StaffType.Physiotherapist,
        physiotherapist_name,
        physiotherapist_birth_date,
        physiotherapist_address,
        physiotherapist_place_of_birth,
        physiotherapist_fiscal_number,
        file_dict,
        "physiotherapist",
    )
    first_deputy_id = create_staff_member(
        StaffType.GameDeputy,
        first_deputy_name,
        first_deputy_birth_date,
        first_deputy_address,
        first_deputy_place_of_birth,
        first_deputy_fiscal_number,
        file_dict,
        "first_deputy",
    )
    second_deputy_id = create_staff_member(
        StaffType.GameDeputy,
        second_deputy_name,
        second_deputy_birth_date,
        second_deputy_address,
        second_deputy_place_of_birth,
        second_deputy_fiscal_number,
        file_dict,
        "second_deputy",
    )

    player_ids = create_players(players, file_dict)

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
    logger.info(f"Team registered: {name} (id: {result.inserted_id})")

    return team_to_dto(team_data)


@router.get("", response_model=List[TeamDto])
async def get_teams():
    teams = await db.db[TEAMS_COLLECTION].find().to_list(1000)
    logger.info(f"Retrieved {len(teams)} teams")
    return [team_to_dto(team) for team in teams]


async def get_team(team_id: str) -> dict:
    """Retrieve a single team by its ID. Used by other routes."""
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")
    return team
