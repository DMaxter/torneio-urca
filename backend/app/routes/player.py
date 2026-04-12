from datetime import datetime
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from database import db, PLAYERS_COLLECTION
from app.schemas.schemas import CreatePlayerDto, PlayerDto
from app.error import Error
from app.utils.auth import get_current_user, require_manage_players
from app.utils import (
    get_logger,
    sanitize_for_serialization,
    calculate_age,
    upload_single_file,
)
from app.constants import MIN_AGE

router = APIRouter(prefix="/players", tags=["Players"])


def player_to_dto(player: dict) -> PlayerDto:
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
        is_goalkeeper=clean.get("is_goalkeeper", False),
    )


@router.post("", response_model=PlayerDto, status_code=201)
async def add_player(
    player: CreatePlayerDto, current_user=Depends(require_manage_players)
):
    get_logger().info(f"[{current_user['username']}] Creating player '{player.name}'")
    player_dict = player.model_dump()
    result = await db.db[PLAYERS_COLLECTION].insert_one(player_dict)
    player_dict["_id"] = result.inserted_id
    get_logger().info(
        f"[{current_user['username']}] Player '{player.name}' created successfully"
    )
    return player_to_dto(player_dict)


@router.post("/admin", response_model=PlayerDto, status_code=201)
async def add_player_admin(
    team: str = Form(...),
    name: str = Form(...),
    birth_date: str = Form(...),
    tournament: str = Form(...),
    fiscal_number: str = Form(""),
    address: str = Form(""),
    place_of_birth: str = Form(""),
    is_federated: bool = Form(False),
    federation_team: str | None = Form(None),
    federation_exams_up_to_date: bool = Form(False),
    is_goalkeeper: bool = Form(False),
    citizen_card: UploadFile | None = File(None),
    proof_of_residency: UploadFile | None = File(None),
    authorization: UploadFile | None = File(None),
    current_user=Depends(require_manage_players),
):
    get_logger().info(
        f"[{current_user['username']}] Creating player '{name}' for team '{team}'"
    )

    player_birth_date = datetime.fromisoformat(birth_date.replace("Z", "+00:00"))
    age = calculate_age(player_birth_date)

    if age < MIN_AGE and authorization is None:
        raise HTTPException(
            status_code=400,
            detail=f"O jogador {name} é menor de {MIN_AGE} anos e requer autorização parental",
        )

    file_dict = {}

    if citizen_card:
        file_id = await upload_single_file(
            citizen_card,
            f"admin_{team}_{name}_citizen_card",
        )
        file_dict["citizen_card_file_id"] = file_id

    if proof_of_residency:
        file_id = await upload_single_file(
            proof_of_residency,
            f"admin_{team}_{name}_proof_of_residency",
        )
        file_dict["proof_of_residency_file_id"] = file_id

    if authorization:
        file_id = await upload_single_file(
            authorization,
            f"admin_{team}_{name}_authorization",
        )
        file_dict["authorization_file_id"] = file_id

    player_dict = {
        "name": name,
        "birth_date": player_birth_date,
        "fiscal_number": fiscal_number,
        "address": address,
        "place_of_birth": place_of_birth,
        "is_federated": is_federated,
        "federation_team": federation_team,
        "federation_exams_up_to_date": federation_exams_up_to_date,
        "is_confirmed": False,
        "is_goalkeeper": is_goalkeeper,
        **file_dict,
    }
    result = await db.db[PLAYERS_COLLECTION].insert_one(player_dict)
    player_dict["_id"] = result.inserted_id

    from app.routes.team import get_team

    get_logger().info(f"Adding player to team '{team}'")
    team_doc = await get_team(team)
    player_id_str = str(result.inserted_id)
    if player_id_str not in team_doc["players"]:
        from database import db as database_db

        await database_db.db["teams"].update_one(
            {"_id": ObjectId(team)},
            {"$push": {"players": player_id_str}},
        )

    get_logger().info(
        f"[{current_user['username']}] Player '{name}' created and added to team successfully"
    )
    return player_to_dto(player_dict)


@router.get("", response_model=List[PlayerDto])
async def get_players(team: str | None = None):
    get_logger().info(f"Retrieving all players (team filter: {team})")
    query = {}
    player_team_map = {}

    if team:
        team_doc = await db.db["teams"].find_one(
            {"_id": ObjectId(team)}, {"players": 1}
        )
        player_ids = team_doc.get("players", []) if team_doc else []
        query["_id"] = {"$in": player_ids}

    players = await db.db[PLAYERS_COLLECTION].find(query).to_list(1000)

    if not team:
        all_teams = await db.db["teams"].find().to_list(1000)
        for t in all_teams:
            for pid in t.get("players", []):
                player_team_map[str(pid)] = str(t["_id"])

    for player in players:
        player["team"] = player_team_map.get(str(player["_id"]))

    get_logger().info(f"Retrieved {len(players)} players")
    return [player_to_dto(player) for player in players]


@router.get("/{player_id}", response_model=PlayerDto)
async def _get_player(player_id: str):
    get_logger().info(f"Retrieving player '{player_id}'")
    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")
    return player_to_dto(player)


@router.patch("/{player_id}/confirm", response_model=PlayerDto)
async def confirm_player(player_id: str, current_user=Depends(require_manage_players)):
    get_logger().info(f"[{current_user['username']}] Confirming player '{player_id}'")
    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")

    try:
        result = await db.db[PLAYERS_COLLECTION].find_one_and_update(
            {"_id": ObjectId(player_id)},
            {
                "$set": {
                    "is_confirmed": True,
                }
            },
            return_document=True,
        )
    except Exception:
        raise Error.invalid_id("player")

    get_logger().info(
        f"[{current_user['username']}] Player '{player_id}' confirmed successfully"
    )
    return player_to_dto(result)


@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: str, current_user=Depends(require_manage_players)):
    get_logger().info(f"[{current_user['username']}] Deleting player '{player_id}'")
    try:
        result = await db.db[PLAYERS_COLLECTION].delete_one(
            {"_id": ObjectId(player_id)}
        )
    except Exception:
        raise Error.invalid_id("player")
    if result.deleted_count == 0:
        raise Error.not_found("Player")

    from database import db as database_db

    player_oid = ObjectId(player_id)

    await database_db.db["teams"].update_many(
        {"players": player_oid}, {"$pull": {"players": player_oid}}
    )

    get_logger().info(
        f"[{current_user['username']}] Player '{player_id}' deleted successfully"
    )


@router.put("/{player_id}", response_model=PlayerDto)
async def update_player(
    player_id: str,
    player_data: CreatePlayerDto,
    current_user=Depends(require_manage_players),
):
    get_logger().info(f"[{current_user['username']}] Updating player '{player_id}'")
    try:
        existing_player = await db.db[PLAYERS_COLLECTION].find_one(
            {"_id": ObjectId(player_id)}
        )
    except Exception:
        raise Error.invalid_id("player")
    if not existing_player:
        raise Error.not_found("Player")

    player_dict = player_data.model_dump()
    await db.db[PLAYERS_COLLECTION].update_one(
        {"_id": ObjectId(player_id)}, {"$set": player_dict}
    )

    updated_player = await db.db[PLAYERS_COLLECTION].find_one(
        {"_id": ObjectId(player_id)}
    )
    get_logger().info(f"Player '{player_id}' updated successfully")

    return player_to_dto(updated_player)


async def get_player(player_id: str) -> dict:
    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")
    return player
