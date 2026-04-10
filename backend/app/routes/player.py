from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from database import db, PLAYERS_COLLECTION
from app.schemas.schemas import CreatePlayerDto, CreateAdminPlayerDto, PlayerDto
from app.error import Error
from app.utils.auth import get_current_user
from app.utils import get_logger, sanitize_for_serialization

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
    )


@router.post("", response_model=PlayerDto, status_code=201)
async def add_player(player: CreatePlayerDto, current_user=Depends(get_current_user)):
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
    player_data: CreateAdminPlayerDto,
    current_user=Depends(get_current_user),
):
    get_logger().info(
        f"[{current_user['username']}] Creating player '{player_data.name}' for team '{player_data.team}'"
    )
    player_dict = {
        "name": player_data.name,
        "birth_date": player_data.birth_date,
        "fiscal_number": "",
        "is_federated": player_data.is_federated,
        "federation_team": player_data.federation_team,
        "federation_exams_up_to_date": False,
        "is_confirmed": True,
    }
    result = await db.db[PLAYERS_COLLECTION].insert_one(player_dict)
    player_dict["_id"] = result.inserted_id

    from app.routes.team import get_team

    get_logger().info(f"Adding player to team '{player_data.team}'")
    team = await get_team(player_data.team)
    player_id_str = str(result.inserted_id)
    if player_id_str not in team["players"]:
        from database import db as database_db

        await database_db.db["teams"].update_one(
            {"_id": ObjectId(player_data.team)},
            {"$push": {"players": player_id_str}},
        )

    get_logger().info(
        f"[{current_user['username']}] Player '{player_data.name}' created and added to team successfully"
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
async def confirm_player(player_id: str, current_user=Depends(get_current_user)):
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
async def delete_player(player_id: str, current_user=Depends(get_current_user)):
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
    player_id: str, player_data: CreatePlayerDto, current_user=Depends(get_current_user)
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
