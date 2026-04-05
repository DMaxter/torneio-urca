from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, TOURNAMENTS_COLLECTION, TEAMS_COLLECTION
from app.schemas.schemas import CreateTournamentDto, TournamentDto
from app.utils.auth import get_current_user
from app.utils import get_logger, sanitize_for_serialization

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


def tournament_to_dto(tournament: dict) -> TournamentDto:
    clean = sanitize_for_serialization(tournament)
    return TournamentDto(
        id=clean["_id"],
        name=clean["name"],
        teams=clean.get("teams", []),
        games=clean.get("games", []),
        groups=clean.get("groups", []),
        goals=clean.get("goals", []),
        cards=clean.get("cards", []),
    )


@router.post("", response_model=TournamentDto, status_code=201)
async def add_tournament(
    tournament: CreateTournamentDto, current_user=Depends(get_current_user)
):
    get_logger().info(
        f"[{current_user['username']}] Creating tournament '{tournament.name}'"
    )
    tournament_dict = {
        "name": tournament.name,
        "teams": [],
        "games": [],
        "groups": [],
        "goals": [],
        "cards": [],
    }
    result = await db.db[TOURNAMENTS_COLLECTION].insert_one(tournament_dict)
    tournament_dict["_id"] = result.inserted_id
    get_logger().info(
        f"[{current_user['username']}] Tournament '{tournament.name}' created successfully"
    )
    return tournament_to_dto(tournament_dict)


@router.get("", response_model=List[TournamentDto])
async def get_tournaments():
    get_logger().info("Retrieving all tournaments")
    tournaments = await db.db[TOURNAMENTS_COLLECTION].find().to_list(1000)
    get_logger().info(f"Retrieved {len(tournaments)} tournaments")
    return [tournament_to_dto(t) for t in tournaments]


@router.delete("/{tournament_id}", status_code=204)
async def delete_tournament(tournament_id: str, current_user=Depends(get_current_user)):
    from app.error import Error

    tournament = await get_tournament(tournament_id)
    # Block if any team in this tournament has players
    teams = (
        await db.db[TEAMS_COLLECTION]
        .find({"tournament": ObjectId(tournament_id)})
        .to_list(1000)
    )
    if any(len(t.get("players", [])) > 0 for t in teams):
        raise Error.bad_request(
            "Não é possível eliminar um torneio com jogadores associados"
        )
    await db.db[TOURNAMENTS_COLLECTION].delete_one({"_id": tournament["_id"]})
    get_logger().info(
        f"[{current_user['username']}] Deleted tournament '{tournament_id}'"
    )


async def get_tournament(tournament_id: str) -> dict:
    from app.error import Error

    try:
        tournament = await db.db[TOURNAMENTS_COLLECTION].find_one(
            {"_id": ObjectId(tournament_id)}
        )
    except Exception:
        raise Error.invalid_id("torneio")
    if not tournament:
        raise Error.not_found("Torneio")
    return tournament
