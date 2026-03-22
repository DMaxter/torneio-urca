import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, TOURNAMENTS_COLLECTION
from app.schemas.schemas import CreateTournamentDto, TournamentDto
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


def tournament_to_dto(tournament: dict) -> TournamentDto:
    return TournamentDto(
        id=str(tournament["_id"]),
        name=tournament["name"],
        teams=[str(t) for t in tournament.get("teams", [])],
        games=[str(g) for g in tournament.get("games", [])],
        groups=[str(g) for g in tournament.get("groups", [])],
        goals=tournament.get("goals", []),
        cards=tournament.get("cards", []),
    )


@router.post("", response_model=TournamentDto, status_code=201)
async def add_tournament(
    tournament: CreateTournamentDto, current_user=Depends(get_current_user)
):
    logger.info(f"[{current_user['username']}] Creating tournament: {tournament.name}")
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
    logger.info(f"Tournament created: {tournament.name} (id: {result.inserted_id})")
    return tournament_to_dto(tournament_dict)


@router.get("", response_model=List[TournamentDto])
async def get_tournaments():
    tournaments = await db.db[TOURNAMENTS_COLLECTION].find().to_list(1000)
    logger.info(f"Retrieved {len(tournaments)} tournaments")
    return [tournament_to_dto(t) for t in tournaments]


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
