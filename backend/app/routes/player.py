from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from database import db, PLAYERS_COLLECTION
from app.schemas.schemas import CreatePlayerDto, PlayerDto
from app.error import Error

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
async def add_player(player: CreatePlayerDto):
    player_dict = player.model_dump()
    result = await db.db[PLAYERS_COLLECTION].insert_one(player_dict)
    player_dict["_id"] = result.inserted_id
    return player_to_dto(player_dict)


@router.get("", response_model=List[PlayerDto])
async def get_players():
    players = await db.db[PLAYERS_COLLECTION].find().to_list(1000)
    return [player_to_dto(player) for player in players]


@router.get("/{player_id}", response_model=PlayerDto)
async def _get_player(player_id: str):
    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")
    return player_to_dto(player)


@router.patch("/{player_id}/confirm", response_model=PlayerDto)
async def confirm_player(player_id: str):
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
    return player_to_dto(result)


async def get_player(player_id: str) -> dict:
    try:
        player = await db.db[PLAYERS_COLLECTION].find_one({"_id": ObjectId(player_id)})
    except Exception:
        raise Error.invalid_id("player")
    if not player:
        raise Error.not_found("Player")
    return player
