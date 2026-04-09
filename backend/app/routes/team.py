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
from app.schemas.schemas import (
    CreateTeamDto,
    TeamDto,
    StaffType,
    RegisterTeamStartDto,
    RegisterStaffDto,
    RegisterPlayerDto,
    RegisterTeamCompleteDto,
    StaffDto,
    PlayerDto,
)
from app.error import Error
from app.constants import MIN_PLAYERS, MIN_AGE, MAX_FILE_SIZE
from app.utils import calculate_age, get_logger, sanitize_for_serialization
from app.utils.auth import get_current_user
from datetime import datetime
import json

router = APIRouter(prefix="/teams", tags=["Teams"])


def team_to_dto(team: dict) -> TeamDto:
    """Convert a team document from the database to a TeamDto."""
    clean = sanitize_for_serialization(team)
    return TeamDto(
        id=clean["_id"],
        tournament=clean["tournament"],
        name=clean["name"],
        responsible_name=clean["responsible_name"],
        responsible_email=clean["responsible_email"],
        responsible_phone=clean["responsible_phone"],
        main_coach=clean["main_coach"],
        assistant_coach=clean.get("assistant_coach"),
        players=clean.get("players", []),
        physiotherapist=clean["physiotherapist"],
        first_deputy=clean["first_deputy"],
        second_deputy=clean.get("second_deputy"),
    )


def staff_to_dto(staff: dict) -> StaffDto:
    """Convert a staff document from the database to a StaffDto."""
    clean = sanitize_for_serialization(staff)
    return StaffDto(
        id=clean["_id"],
        name=clean["name"],
        birth_date=clean["birth_date"],
        address=clean.get("address"),
        place_of_birth=clean.get("place_of_birth"),
        fiscal_number=clean["fiscal_number"],
        staff_type=clean["staff_type"],
        citizen_card_file_id=clean.get("citizen_card_file_id"),
        proof_of_residency_file_id=clean.get("proof_of_residency_file_id"),
        authorization_file_id=clean.get("authorization_file_id"),
    )


def player_to_dto(player: dict) -> PlayerDto:
    """Convert a player document from the database to a PlayerDto."""
    clean = sanitize_for_serialization(player)
    return PlayerDto(
        id=clean["_id"],
        name=clean["name"],
        birth_date=clean["birth_date"],
        address=clean.get("address"),
        place_of_birth=clean.get("place_of_birth"),
        fiscal_number=clean["fiscal_number"],
        citizen_card_file_id=clean.get("citizen_card_file_id"),
        proof_of_residency_file_id=clean.get("proof_of_residency_file_id"),
        authorization_file_id=clean.get("authorization_file_id"),
        is_federated=clean.get("is_federated", False),
        federation_team=clean.get("federation_team"),
        federation_exams_up_to_date=clean.get("federation_exams_up_to_date", False),
        is_confirmed=clean.get("is_confirmed", False),
        team=clean.get("team"),
    )


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object."""
    return datetime.fromisoformat(date_str) if date_str else None


async def process_files(files: List[UploadFile]) -> dict[str, str]:
    """Upload files and return a mapping of filename to file ID."""
    file_dict = {}
    for f in files:
        content = await f.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"O ficheiro '{f.filename}' excede o limite de 5MB",
            )
        filename = f.filename or "unknown"
        content_type = f.content_type or "application/octet-stream"
        file_id = await db.upload_file(filename, content_type, content)
        file_dict[filename] = file_id
    return file_dict


async def upload_single_file(
    file: UploadFile,
    filename: str,
) -> str:
    """Upload a single file with size validation."""
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"O ficheiro '{file.filename}' excede o limite de 5MB",
        )
    content_type = file.content_type or "application/octet-stream"
    return await db.upload_file(filename, content_type, content)


async def create_staff_member(
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
    result = await db.db[STAFF_COLLECTION].insert_one(staff_data)
    return result.inserted_id


async def create_players(players: list, file_dict: dict[str, str]) -> list[ObjectId]:
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
        result = await db.db[PLAYERS_COLLECTION].insert_one(player_data)
        player_ids.append(result.inserted_id)
    return player_ids


@router.post("", response_model=TeamDto, status_code=201)
async def add_team(team: CreateTeamDto, current_user=Depends(get_current_user)):
    """Create a new team by providing full references to existing entities."""
    from app.routes.tournament import get_tournament

    get_logger().info(f"[{current_user['username']}] Creating team '{team.name}'")
    tournament = await get_tournament(team.tournament)
    team_dict = team.model_dump()
    team_dict["tournament"] = ObjectId(team.tournament)
    team_dict["main_coach"] = (
        ObjectId(team.main_coach)
        if team.main_coach
        and team.main_coach not in (None, "None", "")
        and team.main_coach.strip()
        else None
    )
    team_dict["assistant_coach"] = (
        ObjectId(team.assistant_coach)
        if team.assistant_coach
        and team.assistant_coach not in (None, "None", "")
        and team.assistant_coach.strip()
        else None
    )
    team_dict["players"] = (
        [ObjectId(p) for p in team.players if p and p not in (None, "None", "")]
        if team.players
        else []
    )
    team_dict["physiotherapist"] = (
        ObjectId(team.physiotherapist)
        if team.physiotherapist
        and team.physiotherapist not in (None, "None", "")
        and team.physiotherapist.strip()
        else None
    )
    team_dict["first_deputy"] = (
        ObjectId(team.first_deputy)
        if team.first_deputy
        and team.first_deputy not in (None, "None", "")
        and team.first_deputy.strip()
        else None
    )
    team_dict["second_deputy"] = (
        ObjectId(team.second_deputy)
        if team.second_deputy
        and team.second_deputy not in (None, "None", "")
        and team.second_deputy.strip()
        else None
    )
    team_dict["valid"] = False

    result = await db.db[TEAMS_COLLECTION].insert_one(team_dict)

    get_logger().info(f"Adding team '{team.name}' to tournament '{tournament['name']}'")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"teams": result.inserted_id}}
    )
    get_logger().info(
        f"[{current_user['username']}] Team '{team.name}' created successfully"
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

    get_logger().info(f"Starting team registration for '{name}'")
    players = json.loads(players_json)
    if len(players) < MIN_PLAYERS:
        raise HTTPException(
            status_code=400, detail=f"É necessário um mínimo de {MIN_PLAYERS} jogadores"
        )

    get_logger().info("Validating tournament and processing files")
    await get_tournament(tournament)
    file_dict = await process_files(files)

    get_logger().info("Creating staff members")
    main_coach_id = await create_staff_member(
        StaffType.Coach,
        main_coach_name,
        main_coach_birth_date,
        main_coach_address,
        main_coach_place_of_birth,
        main_coach_fiscal_number,
        file_dict,
        "main_coach",
    )
    physiotherapist_id = await create_staff_member(
        StaffType.Physiotherapist,
        physiotherapist_name,
        physiotherapist_birth_date,
        physiotherapist_address,
        physiotherapist_place_of_birth,
        physiotherapist_fiscal_number,
        file_dict,
        "physiotherapist",
    )
    first_deputy_id = await create_staff_member(
        StaffType.GameDeputy,
        first_deputy_name,
        first_deputy_birth_date,
        first_deputy_address,
        first_deputy_place_of_birth,
        first_deputy_fiscal_number,
        file_dict,
        "first_deputy",
    )
    second_deputy_id = await create_staff_member(
        StaffType.GameDeputy,
        second_deputy_name,
        second_deputy_birth_date,
        second_deputy_address,
        second_deputy_place_of_birth,
        second_deputy_fiscal_number,
        file_dict,
        "second_deputy",
    )

    get_logger().info("Creating players")
    player_ids = await create_players(players, file_dict)

    get_logger().info(f"Inserting team '{name}' into database")
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

    get_logger().info(f"Adding team '{name}' to tournament")
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": ObjectId(tournament)}, {"$push": {"teams": result.inserted_id}}
    )
    get_logger().info(f"Team '{name}' registered successfully")

    return team_to_dto(team_data)


@router.post("/register/start", response_model=TeamDto, status_code=201)
async def register_team_start(data: RegisterTeamStartDto):
    """
    Start team registration - creates team with basic info and responsible.

    This is the first step in the multi-step registration flow.
    Returns the created team with a temporary ID.
    """
    from app.routes.tournament import get_tournament

    get_logger().info(f"Starting team registration for '{data.name}'")
    await get_tournament(data.tournament)

    team_data = {
        "tournament": ObjectId(data.tournament),
        "name": data.name,
        "responsible_name": data.responsible_name,
        "responsible_email": data.responsible_email,
        "responsible_phone": data.responsible_phone,
        "players": [],
        "main_coach": None,
        "physiotherapist": None,
        "first_deputy": None,
        "second_deputy": None,
        "valid": False,
        "registration_status": "in_progress",
    }

    result = await db.db[TEAMS_COLLECTION].insert_one(team_data)
    team_data["_id"] = result.inserted_id

    get_logger().info(
        f"Team registration started: '{data.name}' (ID: {result.inserted_id})"
    )
    return team_to_dto(team_data)


@router.post("/register/staff", response_model=StaffDto, status_code=201)
async def register_add_staff(
    staff_type: StaffType = Form(...),
    team_id: str = Form(...),
    name: str = Form(...),
    birth_date: str = Form(...),
    address: Optional[str] = Form(None),
    place_of_birth: Optional[str] = Form(None),
    fiscal_number: str = Form(...),
    citizen_card: Optional[UploadFile] = File(None),
    proof_of_residency: Optional[UploadFile] = File(None),
):
    """
    Add a staff member to a team during registration.

    This is the second step in the multi-step registration flow.
    """
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    file_dict = {}
    if citizen_card:
        file_id = await upload_single_file(
            citizen_card,
            f"staff_{team_id}_{staff_type}_citizen_card",
        )
        file_dict["citizen_card_file_id"] = file_id

    if proof_of_residency:
        file_id = await upload_single_file(
            proof_of_residency,
            f"staff_{team_id}_{staff_type}_proof_of_residency",
        )
        file_dict["proof_of_residency_file_id"] = file_id

    staff_data = {
        "name": name,
        "birth_date": datetime.fromisoformat(birth_date),
        "address": address,
        "place_of_birth": place_of_birth,
        "fiscal_number": fiscal_number,
        "staff_type": staff_type,
        **file_dict,
    }
    result = await db.db[STAFF_COLLECTION].insert_one(staff_data)
    staff_data["_id"] = result.inserted_id

    staff_field_map = {
        StaffType.Coach: "main_coach",
        StaffType.Physiotherapist: "physiotherapist",
        StaffType.GameDeputy: None,
    }
    staff_field = staff_field_map.get(staff_type)
    if staff_field:
        await db.db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)}, {"$set": {staff_field: result.inserted_id}}
        )
    else:
        current_deputy_count = sum(
            1 for d in ["first_deputy", "second_deputy"] if team.get(d)
        )
        if current_deputy_count == 0:
            await db.db[TEAMS_COLLECTION].update_one(
                {"_id": ObjectId(team_id)},
                {"$set": {"first_deputy": result.inserted_id}},
            )
        else:
            await db.db[TEAMS_COLLECTION].update_one(
                {"_id": ObjectId(team_id)},
                {"$set": {"second_deputy": result.inserted_id}},
            )

    get_logger().info(f"Staff '{name}' added to team '{team_id}'")
    return staff_to_dto(staff_data)


@router.post("/register/player", response_model=PlayerDto, status_code=201)
async def register_add_player(
    team_id: str = Form(...),
    name: str = Form(...),
    birth_date: str = Form(...),
    fiscal_number: str = Form(...),
    address: Optional[str] = Form(None),
    place_of_birth: Optional[str] = Form(None),
    is_federated: bool = Form(False),
    federation_team: Optional[str] = Form(None),
    federation_exams_up_to_date: bool = Form(False),
    citizen_card: Optional[UploadFile] = File(None),
    proof_of_residency: Optional[UploadFile] = File(None),
    authorization: Optional[UploadFile] = File(None),
):
    """
    Add a player to a team during registration.

    This is part of the multi-step registration flow.
    Validates age and requires authorization file for minors under MIN_AGE.
    """
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    player_birth_date = datetime.fromisoformat(birth_date.replace("Z", "+00:00"))
    age = calculate_age(player_birth_date)

    file_dict = {}

    if citizen_card:
        file_id = await upload_single_file(
            citizen_card,
            f"player_{team_id}_{name}_citizen_card",
        )
        file_dict["citizen_card_file_id"] = file_id

    if proof_of_residency:
        file_id = await upload_single_file(
            proof_of_residency,
            f"player_{team_id}_{name}_proof_of_residency",
        )
        file_dict["proof_of_residency_file_id"] = file_id

    if authorization:
        file_id = await upload_single_file(
            authorization,
            f"player_{team_id}_{name}_authorization",
        )
        file_dict["authorization_file_id"] = file_id

    if age < MIN_AGE and "authorization_file_id" not in file_dict:
        raise HTTPException(
            status_code=400,
            detail=f"O jogador {name} é menor de {MIN_AGE} anos e requer autorização",
        )

    if is_federated and not federation_team:
        raise HTTPException(
            status_code=400,
            detail=f"O jogador {name} é federado e requer a equipa federada",
        )

    player_data = {
        "name": name,
        "birth_date": player_birth_date,
        "address": address,
        "place_of_birth": place_of_birth,
        "fiscal_number": fiscal_number,
        "is_federated": is_federated,
        "federation_team": federation_team,
        "federation_exams_up_to_date": federation_exams_up_to_date,
        "is_confirmed": False,
        "team": ObjectId(team_id),
        **file_dict,
    }

    result = await db.db[PLAYERS_COLLECTION].insert_one(player_data)
    player_data["_id"] = result.inserted_id

    await db.db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)}, {"$push": {"players": result.inserted_id}}
    )

    get_logger().info(f"Player '{name}' added to team '{team_id}'")
    return player_to_dto(player_data)


@router.post("/register/complete", response_model=TeamDto, status_code=200)
async def register_complete(data: RegisterTeamCompleteDto):
    """
    Complete team registration.

    This is the final step that validates minimum player count and adds
    the team to the tournament.
    """
    from app.routes.tournament import get_tournament

    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(data.team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    if len(team.get("players", [])) < MIN_PLAYERS:
        raise HTTPException(
            status_code=400, detail=f"É necessário um mínimo de {MIN_PLAYERS} jogadores"
        )

    await db.db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(data.team_id)}, {"$set": {"registration_status": "completed"}}
    )

    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": team["tournament"]}, {"$push": {"teams": ObjectId(data.team_id)}}
    )

    updated_team = await db.db[TEAMS_COLLECTION].find_one(
        {"_id": ObjectId(data.team_id)}
    )
    get_logger().info(f"Team '{team['name']}' registration completed")
    return team_to_dto(updated_team)


@router.delete("/register/{team_id}", status_code=204)
async def cancel_registration(team_id: str):
    """
    Cancel a team registration and delete all associated records.

    Used to cleanup if the user abandons the registration process.
    """
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    player_ids = team.get("players", [])
    if player_ids:
        await db.db[PLAYERS_COLLECTION].delete_many({"_id": {"$in": player_ids}})

    staff_ids = [
        team.get("main_coach"),
        team.get("physiotherapist"),
        team.get("first_deputy"),
        team.get("second_deputy"),
    ]
    staff_ids = [s for s in staff_ids if s]
    if staff_ids:
        await db.db[STAFF_COLLECTION].delete_many({"_id": {"$in": staff_ids}})

    await db.db[TEAMS_COLLECTION].delete_one({"_id": ObjectId(team_id)})
    get_logger().info(f"Registration cancelled for team '{team_id}'")


@router.get("", response_model=List[TeamDto])
async def get_teams():
    get_logger().info("Retrieving all teams")
    teams = await db.db[TEAMS_COLLECTION].find().to_list(1000)

    for team in teams:
        player_ids = team.get("players", [])
        if player_ids:
            valid_player_ids = []
            for pid in player_ids:
                if isinstance(pid, ObjectId):
                    exists = await db.db[PLAYERS_COLLECTION].find_one({"_id": pid})
                    if exists:
                        valid_player_ids.append(pid)
                elif isinstance(pid, str):
                    try:
                        pid_oid = ObjectId(pid)
                        exists = await db.db[PLAYERS_COLLECTION].find_one(
                            {"_id": pid_oid}
                        )
                        if exists:
                            valid_player_ids.append(pid_oid)
                    except Exception:
                        pass

            if len(valid_player_ids) != len(player_ids):
                await db.db[TEAMS_COLLECTION].update_one(
                    {"_id": team["_id"]}, {"$set": {"players": valid_player_ids}}
                )
                get_logger().info(
                    f"Cleaned up team '{team.get('name')}': {len(player_ids)} -> {len(valid_player_ids)} players"
                )
                team["players"] = valid_player_ids

    get_logger().info(f"Retrieved {len(teams)} teams")
    return [team_to_dto(team) for team in teams]


async def get_team(team_id: str) -> dict:
    """Retrieve a single team by its ID. Used by other routes."""
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception as e:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")
    get_logger().info(f"Team players field: {team.get('players')}")
    get_logger().info(f"Team players type: {type(team.get('players'))}")
    return team


@router.get("/{team_id}", response_model=TeamDto)
async def get_team_endpoint(team_id: str):
    """Retrieve a single team by its ID."""
    get_logger().info(f"Retrieving team '{team_id}'")
    team = await get_team(team_id)
    return team_to_dto(team)


@router.get("/{team_id}/players")
async def get_team_players(team_id: str):
    """Retrieve all players belonging to a team."""
    get_logger().info(f"Retrieving players for team '{team_id}'")
    team = await get_team(team_id)
    player_ids = team.get("players", [])

    get_logger().info(f"Team: {team.get('name')}, Player IDs: {player_ids}")

    if not player_ids:
        return []

    player_ids_converted = []
    for pid in player_ids:
        if isinstance(pid, ObjectId):
            player_ids_converted.append(pid)
        elif isinstance(pid, str):
            try:
                player_ids_converted.append(ObjectId(pid))
            except Exception:
                get_logger().warning(f"Invalid player ID format: {pid}")
        else:
            get_logger().warning(f"Unknown player ID type: {type(pid)}")

    get_logger().info(f"Converted player IDs: {player_ids_converted}")

    try:
        players = (
            await db.db[PLAYERS_COLLECTION]
            .find({"_id": {"$in": player_ids_converted}})
            .to_list(1000)
        )
    except Exception as e:
        get_logger().error(f"Error querying players: {e}")
        return []

    get_logger().info(f"Found {len(players)} players")

    from app.routes.player import player_to_dto

    return [player_to_dto(player) for player in players]


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: str, current_user=Depends(get_current_user)):
    """Delete a team and all its players."""
    get_logger().info(f"[{current_user['username']}] Deleting team '{team_id}'")
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    player_ids = team.get("players", [])
    if player_ids:
        player_ids_converted = []
        for pid in player_ids:
            if isinstance(pid, ObjectId):
                player_ids_converted.append(pid)
            elif isinstance(pid, str):
                try:
                    player_ids_converted.append(ObjectId(pid))
                except Exception:
                    pass
        if player_ids_converted:
            await db.db[PLAYERS_COLLECTION].delete_many(
                {"_id": {"$in": player_ids_converted}}
            )
            get_logger().info(f"Deleted {len(player_ids_converted)} players")

    await db.db[TEAMS_COLLECTION].delete_one({"_id": ObjectId(team_id)})
    get_logger().info(f"Team '{team_id}' deleted successfully")


@router.put("/{team_id}", response_model=TeamDto)
async def update_team(
    team_id: str, team: CreateTeamDto, current_user=Depends(get_current_user)
):
    """Update a team."""
    get_logger().info(f"[{current_user['username']}] Updating team '{team_id}'")
    try:
        existing_team = await db.db[TEAMS_COLLECTION].find_one(
            {"_id": ObjectId(team_id)}
        )
    except Exception:
        raise Error.invalid_id("team")
    if not existing_team:
        raise Error.not_found("Team")

    team_dict = team.model_dump()
    team_dict["tournament"] = ObjectId(team.tournament)
    team_dict["main_coach"] = (
        ObjectId(team.main_coach)
        if team.main_coach
        and team.main_coach not in (None, "None", "")
        and team.main_coach.strip()
        else None
    )
    team_dict["assistant_coach"] = (
        ObjectId(team.assistant_coach)
        if team.assistant_coach
        and team.assistant_coach not in (None, "None", "")
        and team.assistant_coach.strip()
        else None
    )
    team_dict["players"] = (
        [ObjectId(p) for p in team.players if p and p not in (None, "None", "")]
        if team.players
        else []
    )
    team_dict["physiotherapist"] = (
        ObjectId(team.physiotherapist)
        if team.physiotherapist
        and team.physiotherapist not in (None, "None", "")
        and team.physiotherapist.strip()
        else None
    )

    await db.db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)}, {"$set": team_dict}
    )

    updated_team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    get_logger().info(f"Team '{team_id}' updated successfully")

    return team_to_dto(updated_team)


@router.post("/{team_id}/players", response_model=TeamDto)
async def add_player_to_team(
    team_id: str, player_id: str, current_user=Depends(get_current_user)
):
    """Add an existing player to a team."""
    get_logger().info(
        f"[{current_user['username']}] Adding player '{player_id}' to team '{team_id}'"
    )
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")

    player_oid = ObjectId(player_id)
    current_players = team.get("players", [])
    if player_oid not in current_players:
        current_players.append(player_oid)
        await db.db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)}, {"$set": {"players": current_players}}
        )
        # Also update the player's team reference
        await db.db[PLAYERS_COLLECTION].update_one(
            {"_id": player_oid}, {"$set": {"team": ObjectId(team_id)}}
        )

    updated_team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    return team_to_dto(updated_team)


@router.delete("/{team_id}/players/{player_id}", response_model=TeamDto)
async def remove_player_from_team(
    team_id: str, player_id: str, current_user=Depends(get_current_user)
):
    """Remove a player from a team."""
    get_logger().info(
        f"[{current_user['username']}] Removing player '{player_id}' from team '{team_id}'"
    )
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    player_oid = ObjectId(player_id)
    current_players = team.get("players", [])
    current_players = [p for p in current_players if p != player_oid]
    await db.db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)}, {"$set": {"players": current_players}}
    )
    # Clear the player's team reference
    await db.db[PLAYERS_COLLECTION].update_one(
        {"_id": player_oid}, {"$set": {"team": None}}
    )

    updated_team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    return team_to_dto(updated_team)


@router.patch("/{team_id}/staff/{staff_field}", response_model=TeamDto)
async def update_team_staff(
    team_id: str,
    staff_field: str,
    staff_id: Optional[str] = None,
    current_user=Depends(get_current_user),
):
    """Update a team's staff member (set or remove)."""
    valid_fields = [
        "main_coach",
        "assistant_coach",
        "physiotherapist",
        "first_deputy",
        "second_deputy",
    ]
    if staff_field not in valid_fields:
        raise Error.bad_request(
            f"Invalid staff field. Must be one of: {', '.join(valid_fields)}"
        )

    get_logger().info(
        f"[{current_user['username']}] Updating {staff_field} for team '{team_id}'"
    )
    try:
        team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    except Exception:
        raise Error.invalid_id("team")
    if not team:
        raise Error.not_found("Team")

    if staff_id:
        try:
            staff = await db.db[STAFF_COLLECTION].find_one({"_id": ObjectId(staff_id)})
        except Exception:
            raise Error.invalid_id("staff")
        if not staff:
            raise Error.not_found("Staff member")
        staff_oid = ObjectId(staff_id)
    else:
        staff_oid = None

    await db.db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)}, {"$set": {staff_field: staff_oid}}
    )

    updated_team = await db.db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    return team_to_dto(updated_team)
