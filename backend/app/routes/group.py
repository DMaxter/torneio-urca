from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import (
    db,
    GROUPS_COLLECTION,
    TOURNAMENTS_COLLECTION,
    GAMES_COLLECTION,
    GAME_CALLS_COLLECTION,
    TEAMS_COLLECTION,
)
from app.schemas.schemas import CreateGroupDto, GroupDto
from app.error import Error
from app.utils.auth import get_current_user, require_manage_games
from app.utils import get_logger, sanitize_for_serialization
from app.models.models import GameStatus

router = APIRouter(prefix="/groups", tags=["Groups"])


def group_to_dto(group: dict) -> GroupDto:
    clean = sanitize_for_serialization(group)
    return GroupDto(
        id=clean["_id"],
        tournament=clean["tournament"],
        name=clean["name"],
        teams=clean.get("teams", []),
    )


@router.post("", response_model=GroupDto, status_code=201)
async def add_group(group: CreateGroupDto, current_user = Depends(require_manage_games)):
    from app.routes.tournament import get_tournament

    get_logger().info(f"[{current_user['username']}] Creating group '{group.name}'")
    tournament = await get_tournament(group.tournament)
    group_dict = group.model_dump()
    group_dict["tournament"] = ObjectId(group.tournament)
    team_object_ids = [ObjectId(t) for t in group.teams]

    existing_groups = (
        await db.db[GROUPS_COLLECTION]
        .find(
            {
                "tournament": ObjectId(group.tournament),
                "teams": {"$in": team_object_ids},
            }
        )
        .to_list(100)
    )

    if existing_groups:
        teams_in_groups = set()
        for g in existing_groups:
            for t in g.get("teams", []):
                teams_in_groups.add(str(t))

        conflicting_teams = [t for t in group.teams if t in teams_in_groups]
        if conflicting_teams:
            raise Error.bad_request(
                "Uma ou mais equipas já pertencem a outro grupo neste torneios"
            )

    group_dict["teams"] = team_object_ids

    result = await db.db[GROUPS_COLLECTION].insert_one(group_dict)

    get_logger().info(
        f"Adding group '{group.name}' to tournament '{tournament['name']}'"
    )
    await db.db[TOURNAMENTS_COLLECTION].update_one(
        {"_id": tournament["_id"]}, {"$push": {"groups": result.inserted_id}}
    )
    get_logger().info(
        f"[{current_user['username']}] Group '{group.name}' created successfully"
    )

    return group_to_dto(group_dict)


@router.get("", response_model=List[GroupDto])
async def get_groups():
    get_logger().info("Retrieving all groups")
    groups = await db.db[GROUPS_COLLECTION].find().to_list(1000)
    get_logger().info(f"Retrieved {len(groups)} groups")
    return [group_to_dto(group) for group in groups]


@router.put("/{group_id}", response_model=GroupDto)
async def update_group(
    group_id: str, group: CreateGroupDto, current_user=Depends(require_manage_games)
):
    from app.routes.tournament import get_tournament

    try:
        existing_group = await db.db[GROUPS_COLLECTION].find_one(
            {"_id": ObjectId(group_id)}
        )
    except Exception:
        raise Error.invalid_id("group")
    if not existing_group:
        raise Error.not_found("Group")

    tournament = await get_tournament(group.tournament)
    team_object_ids = [ObjectId(t) for t in group.teams]

    existing_groups = (
        await db.db[GROUPS_COLLECTION]
        .find(
            {
                "tournament": ObjectId(group.tournament),
                "teams": {"$in": team_object_ids},
                "_id": {"$ne": ObjectId(group_id)},
            }
        )
        .to_list(100)
    )

    if existing_groups:
        teams_in_groups = set()
        for g in existing_groups:
            for t in g.get("teams", []):
                teams_in_groups.add(str(t))

        conflicting_teams = [t for t in group.teams if t in teams_in_groups]
        if conflicting_teams:
            raise Error.bad_request(
                "Uma ou mais equipas já pertencem a outro grupo neste torneios"
            )

    await db.db[GROUPS_COLLECTION].update_one(
        {"_id": ObjectId(group_id)},
        {"$set": {"name": group.name, "teams": team_object_ids}},
    )

    updated_group = await db.db[GROUPS_COLLECTION].find_one({"_id": ObjectId(group_id)})
    get_logger().info(
        f"[{current_user['username']}] Group '{group_id}' updated successfully"
    )

    return group_to_dto(updated_group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(group_id: str, current_user = Depends(require_manage_games)):
    try:
        group = await db.db[GROUPS_COLLECTION].find_one({"_id": ObjectId(group_id)})
    except Exception:
        raise Error.invalid_id("group")
    if not group:
        raise Error.not_found("Group")

    await db.db[GROUPS_COLLECTION].delete_one({"_id": ObjectId(group_id)})
    get_logger().info(
        f"[{current_user['username']}] Group '{group_id}' deleted successfully"
    )


class TeamStanding(BaseModel):
    team_id: str
    team_name: str
    points: int
    games: int
    wins: int
    ties: int
    losses: int
    goals_scored: int
    goals_suffered: int
    goal_difference: int


class ClassificationDto(BaseModel):
    group_id: str
    group_name: str
    standings: List[TeamStanding]


@router.get("/{group_id}/classification", response_model=ClassificationDto)
async def get_classification(group_id: str):
    try:
        group = await db.db[GROUPS_COLLECTION].find_one({"_id": ObjectId(group_id)})
    except Exception:
        raise Error.invalid_id("group")
    if not group:
        raise Error.not_found("Group")

    team_ids = [str(t) for t in group.get("teams", [])]

    if not team_ids:
        return ClassificationDto(
            group_id=group_id, group_name=group["name"], standings=[]
        )

    teams = (
        await db.db[TEAMS_COLLECTION]
        .find({"_id": {"$in": [ObjectId(t) for t in team_ids]}})
        .to_list(100)
    )
    teams_map = {str(t["_id"]): t["name"] for t in teams}

    games = (
        await db.db[GAMES_COLLECTION]
        .find({"tournament": group["tournament"], "status": GameStatus.Finished})
        .to_list(1000)
    )

    calls = await db.db[GAME_CALLS_COLLECTION].find().to_list(1000)
    calls_map = {str(c["_id"]): c for c in calls}

    standings = {
        team_id: {
            "team_id": team_id,
            "team_name": teams_map.get(team_id, "Unknown"),
            "points": 0,
            "games": 0,
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "goals_scored": 0,
            "goals_suffered": 0,
        }
        for team_id in team_ids
    }

    for game in games:
        home_call = calls_map.get(str(game.get("home_call")))
        away_call = calls_map.get(str(game.get("away_call")))
        if not home_call or not away_call:
            continue

        home_team_id = str(home_call.get("team"))
        away_team_id = str(away_call.get("team"))

        if home_team_id not in team_ids or away_team_id not in team_ids:
            continue

        home_goals = 0
        away_goals = 0
        for event in game.get("events", []):
            if "Goal" in event:
                goal = event["Goal"]
                goal_team_name = goal.get("team_name", "")
                home_team_name = teams_map.get(home_team_id, "")
                away_team_name = teams_map.get(away_team_id, "")
                if goal_team_name == home_team_name:
                    home_goals += 1
                elif goal_team_name == away_team_name:
                    away_goals += 1

        standings[home_team_id]["games"] += 1
        standings[away_team_id]["games"] += 1
        standings[home_team_id]["goals_scored"] += home_goals
        standings[home_team_id]["goals_suffered"] += away_goals
        standings[away_team_id]["goals_scored"] += away_goals
        standings[away_team_id]["goals_suffered"] += home_goals

        if home_goals > away_goals:
            standings[home_team_id]["wins"] += 1
            standings[home_team_id]["points"] += 3
            standings[away_team_id]["losses"] += 1
        elif home_goals < away_goals:
            standings[away_team_id]["wins"] += 1
            standings[away_team_id]["points"] += 3
            standings[home_team_id]["losses"] += 1
        else:
            standings[home_team_id]["ties"] += 1
            standings[away_team_id]["ties"] += 1
            standings[home_team_id]["points"] += 1
            standings[away_team_id]["points"] += 1

    result = []
    for s in standings.values():
        goal_diff = int(s["goals_scored"]) - int(s["goals_suffered"])
        result.append(
            TeamStanding(
                team_id=s["team_id"],
                team_name=s["team_name"],
                points=int(s["points"]),
                games=int(s["games"]),
                wins=int(s["wins"]),
                ties=int(s["ties"]),
                losses=int(s["losses"]),
                goals_scored=int(s["goals_scored"]),
                goals_suffered=int(s["goals_suffered"]),
                goal_difference=goal_diff,
            )
        )

    # Build head-to-head results map for direct confrontation tiebreaker
    h2h_results = {}  # (team_a_id, team_b_id) -> winner team_id or None (tie)
    for game in games:
        home_call = calls_map.get(str(game.get("home_call")))
        away_call = calls_map.get(str(game.get("away_call")))
        if not home_call or not away_call:
            continue
        home_team_id = str(home_call.get("team"))
        away_team_id = str(away_call.get("team"))
        if home_team_id not in team_ids or away_team_id not in team_ids:
            continue
        home_goals = 0
        away_goals = 0
        for event in game.get("events", []):
            if "Goal" in event:
                goal = event["Goal"]
                goal_team_name = goal.get("team_name", "")
                home_team_name = teams_map.get(home_team_id, "")
                away_team_name = teams_map.get(away_team_id, "")
                if goal_team_name == home_team_name:
                    home_goals += 1
                elif goal_team_name == away_team_name:
                    away_goals += 1
        if home_goals > away_goals:
            h2h_results[(home_team_id, away_team_id)] = home_team_id
            h2h_results[(away_team_id, home_team_id)] = home_team_id
        elif away_goals > home_goals:
            h2h_results[(home_team_id, away_team_id)] = away_team_id
            h2h_results[(away_team_id, home_team_id)] = away_team_id
        else:
            h2h_results[(home_team_id, away_team_id)] = None
            h2h_results[(away_team_id, home_team_id)] = None

    def compare_teams(a: TeamStanding, b: TeamStanding) -> int:
        # 1. Points (higher is better)
        if a.points != b.points:
            return b.points - a.points
        # 2. Direct confrontation (head-to-head)
        h2h = h2h_results.get((a.team_id, b.team_id))
        if h2h is not None:
            if h2h == a.team_id:
                return -1  # a wins
            elif h2h == b.team_id:
                return 1  # b wins
        # 3. Goal difference (higher is better)
        if a.goal_difference != b.goal_difference:
            return b.goal_difference - a.goal_difference
        # 4. Goals scored (higher is better)
        if a.goals_scored != b.goals_scored:
            return b.goals_scored - a.goals_scored
        # 5. Goals suffered (lower is better)
        if a.goals_suffered != b.goals_suffered:
            return a.goals_suffered - b.goals_suffered
        return 0

    from functools import cmp_to_key

    result.sort(key=cmp_to_key(compare_teams))

    get_logger().info(f"Retrieved classification for group '{group_id}'")
    return ClassificationDto(
        group_id=group_id, group_name=group["name"], standings=result
    )
