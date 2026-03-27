from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends
from database import db, PLAYERS_COLLECTION
from app.schemas.schemas import CreatePlayerDto, CreateAdminPlayerDto, PlayerDto
from app.error import Error
from app.utils.auth import get_current_user, get_admin_user
from app.utils import get_logger

router = APIRouter(prefix="/players", tags=["Players"])


def player_to_dto(player: dict) -> PlayerDto:
    return PlayerDto(
        id=str(player["_id"]),
        name=player["name"],
        birth_date=player["birth_date"],
        address=player.get("address"),
        place_of_birth=player.get("place_of_birth"),
        fiscal_number=player["fiscal_number"],
        citizen_card_file_id=player.get("citizen_card_file_id"),
        proof_of_residency_file_id=player.get("proof_of_residency_file_id"),
        authorization_file_id=player.get("authorization_file_id"),
        is_federated=player.get("is_federated", False),
        federation_team=player.get("federation_team"),
        federation_exams_up_to_date=player.get("federation_exams_up_to_date", False),
        is_confirmed=player.get("is_confirmed", False),
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
    current_user=Depends(get_admin_user),
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
async def get_players():
    get_logger().info("Retrieving all players")
    players = await db.db[PLAYERS_COLLECTION].find().to_list(1000)
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
        result = await db.db[PLAYERS_COLLECTION].find_one_and_update(
            {"_id": ObjectId(player_id)},
            {"$set": {"is_confirmed": True}},
            return_document=True,
        )
    except Exception:
        raise Error.invalid_id("player")
    if not result:
        raise Error.not_found("Player")
    get_logger().info(
        f"[{current_user['username']}] Player '{player_id}' confirmed successfully"
    )
    return player_to_dto(result)


@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: str, current_user=Depends(get_admin_user)):
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

    await database_db.db["teams"].update_many(
        {"players": player_id}, {"$pull": {"players": player_id}}
    )

    get_logger().info(
        f"[{current_user['username']}] Player '{player_id}' deleted successfully"
    )


async def get_player(player_id: str) -> dict:
    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")
    return player
