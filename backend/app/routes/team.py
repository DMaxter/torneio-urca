from typing import List
from bson import ObjectId
from fastapi import APIRouter
from database import db, TEAMS_COLLECTION, TOURNAMENTS_COLLECTION
from app.schemas.schemas import CreateTeamDto, TeamDto
from app.error import Error

router = APIRouter(prefix="/teams", tags=["Teams"])


def team_to_dto(team: dict) -> TeamDto:
    return TeamDto(
        id=str(team["_id"]),
        tournament=str(team["tournament"]),
        name=team["name"],
        gender=team["gender"],
        responsible=str(team["responsible"]),
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
    team_dict["responsible"] = ObjectId(team.responsible)
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
