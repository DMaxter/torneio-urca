from typing import Optional
from bson import ObjectId
from fastapi import APIRouter
from pydantic import BaseModel
from database import (
    db,
    TOURNAMENTS_COLLECTION,
    GAMES_COLLECTION,
    GAME_CALLS_COLLECTION,
    GOALS_COLLECTION,
    CARDS_COLLECTION,
    TEAMS_COLLECTION,
    GROUPS_COLLECTION,
)
from app.error import Error
from app.utils import get_logger
from app.models.models import GameStatus

router = APIRouter(prefix="/prizes", tags=["Prizes"])


class BestScorerResult(BaseModel):
    position: int
    player_id: Optional[str] = None
    team_id: str
    player_name: str
    team_name: str
    goals: int
    games: int
    group_position: Optional[int] = None


class BestDefenseResult(BaseModel):
    position: int
    team_id: str
    team_name: str
    goals_suffered: int
    games: int
    group_position: Optional[int] = None


class FairPlayResult(BaseModel):
    position: int
    team_id: str
    team_name: str
    cards: int
    games: int


class PrizesResult(BaseModel):
    best_scorer: list[BestScorerResult] = []
    best_defense: list[BestDefenseResult] = []
    fair_play: list[FairPlayResult] = []


async def calculate_team_standings(
    tournament_id: str,
    group_teams: list,
    games: list,
    calls_map: dict,
    teams_map: dict,
) -> list:
    standings = {}
    for t in group_teams:
        standings[t] = {
            "team_id": t,
            "team_name": teams_map.get(t, {}).get("name", ""),
            "points": 0,
            "games": 0,
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "goals_scored": 0,
            "goals_suffered": 0,
            "fouls": 0,
        }

    for game in games:
        if str(game.get("status")) != str(GameStatus.Finished.value):
            continue

        home_call = calls_map.get(str(game.get("home_call")))
        away_call = calls_map.get(str(game.get("away_call")))
        if not home_call or not away_call:
            continue

        htid = str(home_call.get("team"))
        atid = str(away_call.get("team"))

        if htid not in group_teams or atid not in group_teams:
            continue

        hg = 0
        ag = 0
        fouls_htid = 0
        fouls_atid = 0
        for event in game.get("events", []):
            if "Goal" in event:
                g = event["Goal"]
                gn = g.get("team_name", "")
                htn = teams_map.get(htid, {}).get("name", "")
                atn = teams_map.get(atid, {}).get("name", "")
                if gn == htn:
                    hg += 1
                elif gn == atn:
                    ag += 1
            elif "Foul" in event:
                f = event["Foul"]
                foul_team_id = str(f.get("team_id"))
                if foul_team_id == htid:
                    fouls_htid += 1
                elif foul_team_id == atid:
                    fouls_atid += 1

        standings[htid]["games"] += 1
        standings[atid]["games"] += 1
        standings[htid]["goals_scored"] += hg
        standings[htid]["goals_suffered"] += ag
        standings[atid]["goals_scored"] += ag
        standings[atid]["goals_suffered"] += hg
        standings[htid]["fouls"] += fouls_htid
        standings[atid]["fouls"] += fouls_atid

        if hg > ag:
            standings[htid]["wins"] += 1
            standings[htid]["points"] += 3
            standings[atid]["losses"] += 1
        elif hg < ag:
            standings[atid]["wins"] += 1
            standings[atid]["points"] += 3
            standings[htid]["losses"] += 1
        else:
            standings[htid]["ties"] += 1
            standings[atid]["ties"] += 1
            standings[htid]["points"] += 1
            standings[atid]["points"] += 1

    sorted_standings = sorted(
        standings.values(),
        key=lambda s: (
            (s["points"] / s["games"]) if s["games"] > 0 else 0,
            ((s["goals_scored"] - s["goals_suffered"]) / s["games"])
            if s["games"] > 0
            else 0,
            (s["goals_scored"] / s["games"]) if s["games"] > 0 else 0,
            (s["goals_suffered"] / s["games"])
            if s["games"] > 0
            else float("inf"),  # Lower is better
            (s["fouls"] / s["games"])
            if s["games"] > 0
            else float("inf"),  # Lower is better
        ),
        reverse=True,  # Higher is better for points, goal difference, goals scored
    )
    return sorted_standings


async def is_worse_classification_in_group(
    tournament_id: str,
    team_id: str,
    other_team_name: str,
    games: list,
    calls_map: dict,
    teams_map: dict,
) -> bool:
    team_groups = (
        await db.db[GROUPS_COLLECTION]
        .find({"tournament": ObjectId(tournament_id), "teams": ObjectId(team_id)})
        .to_list(10)
    )

    if not team_groups:
        return False

    group = team_groups[0]
    group_teams = [str(t) for t in group.get("teams", [])]

    if not group_teams:
        return False

    sorted_standings = await calculate_team_standings(
        tournament_id, group_teams, games, calls_map, teams_map
    )

    current_position = None
    other_position = None
    for i, s in enumerate(sorted_standings):
        if s["team_id"] == team_id:
            current_position = i + 1
        if s["team_name"] == other_team_name:
            other_position = i + 1

    if current_position and other_position:
        return current_position > other_position

    return False


async def get_team_group_position(
    tournament_id: str,
    team_id: str,
    games: list,
    calls_map: dict,
    teams_map: dict,
) -> Optional[int]:
    team_groups = (
        await db.db[GROUPS_COLLECTION]
        .find({"tournament": ObjectId(tournament_id), "teams": ObjectId(team_id)})
        .to_list(1)
    )

    if not team_groups:
        return None

    group = team_groups[0]
    group_teams = [str(t) for t in group.get("teams", [])]

    if not group_teams:
        return None

    sorted_standings = await calculate_team_standings(
        tournament_id, group_teams, games, calls_map, teams_map
    )

    # Identify tie groups in standings
    groups = []
    i = 0
    while i < len(sorted_standings):
        group_start = i
        group_size = 1
        for j in range(i + 1, len(sorted_standings)):
            if (
                sorted_standings[j]["points"] == sorted_standings[i]["points"]
                and (
                    sorted_standings[j]["goals_scored"]
                    - sorted_standings[j]["goals_suffered"]
                )
                == (
                    sorted_standings[i]["goals_scored"]
                    - sorted_standings[i]["goals_suffered"]
                )
                and sorted_standings[j]["goals_scored"]
                == sorted_standings[i]["goals_scored"]
            ):
                group_size += 1
            else:
                break
        groups.append({"start": group_start, "size": group_size})
        i += group_size

    # Find position for team
    for idx, s in enumerate(sorted_standings):
        if s["team_id"] == team_id:
            # Find which group this team belongs to
            position = 1
            for g in groups:
                if idx >= g["start"] and idx < g["start"] + g["size"]:
                    for prev_g in groups:
                        if prev_g["start"] < g["start"]:
                            position += prev_g["size"]
                    return position

    return None


async def get_team_group_id(
    tournament_id: str,
    team_id: str,
) -> Optional[str]:
    team_groups = (
        await db.db[GROUPS_COLLECTION]
        .find({"tournament": ObjectId(tournament_id), "teams": ObjectId(team_id)})
        .to_list(1)
    )

    if not team_groups:
        return None

    return str(team_groups[0]["_id"])


@router.get("/{tournament_id}", response_model=PrizesResult)
async def get_prizes(tournament_id: str):
    try:
        tournament = await db.db[TOURNAMENTS_COLLECTION].find_one(
            {"_id": ObjectId(tournament_id)}
        )
    except Exception:
        raise Error.invalid_id("torneio")
    if not tournament:
        raise Error.not_found("Torneio")

    logger = get_logger()
    logger.info(f"Calculating prizes for tournament '{tournament['name']}'")

    team_ids = [str(t) for t in tournament.get("teams", [])]
    if not team_ids:
        return PrizesResult(best_scorer=[], best_defense=[], fair_play=[])

    teams = (
        await db.db[TEAMS_COLLECTION]
        .find({"_id": {"$in": [ObjectId(t) for t in team_ids]}})
        .to_list(100)
    )
    teams_map = {str(t["_id"]): t for t in teams}

    games = (
        await db.db[GAMES_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
                "status": {"$in": [GameStatus.Finished, GameStatus.InProgress]},
            }
        )
        .to_list(1000)
    )

    calls = await db.db[GAME_CALLS_COLLECTION].find().to_list(1000)
    calls_map = {str(c["_id"]): c for c in calls}

    team_games = {t: 0 for t in team_ids}
    goals_for_team = {t: 0 for t in team_ids}
    goals_against_team = {t: 0 for t in team_ids}

    for game in games:
        home_call = calls_map.get(str(game.get("home_call")))
        away_call = calls_map.get(str(game.get("away_call")))
        if not home_call or not away_call:
            continue

        home_team_id = str(home_call.get("team"))
        away_team_id = str(away_call.get("team"))

        if home_team_id not in team_ids or away_team_id not in team_ids:
            continue

        team_games[home_team_id] += 1
        team_games[away_team_id] += 1

        home_goals = 0
        away_goals = 0
        for event in game.get("events", []):
            if "Goal" in event:
                goal = event["Goal"]
                goal_team_name = goal.get("team_name", "")
                home_team_name = teams_map.get(home_team_id, {}).get("name", "")
                away_team_name = teams_map.get(away_team_id, {}).get("name", "")
                if goal_team_name == home_team_name:
                    home_goals += 1
                elif goal_team_name == away_team_name:
                    away_goals += 1

        goals_for_team[home_team_id] += home_goals
        goals_against_team[home_team_id] += away_goals
        goals_for_team[away_team_id] += away_goals
        goals_against_team[away_team_id] += home_goals

    team_group_positions = {}
    for team_id in team_ids:
        pos = await get_team_group_position(
            tournament_id, team_id, games, calls_map, teams_map
        )
        team_group_positions[team_id] = (
            pos if pos is not None else float("inf")
        )  # Use infinity for teams not in a group

    all_goals = (
        await db.db[GOALS_COLLECTION]
        .find({"tournament": ObjectId(tournament_id), "player_id": {"$ne": None}})
        .to_list(10000)
    )

    player_goals = {}
    for goal in all_goals:
        player_id = str(goal.get("player_id"))
        if player_id not in player_goals:
            player_goals[player_id] = 0
        player_goals[player_id] += 1

    players_map = {}
    player_names_map = {}
    for team in teams:
        for player_id in team.get("players", []):
            players_map[str(player_id)] = {
                "player_id": str(player_id),
                "team_id": str(team["_id"]),
                "team_name": team["name"],
            }

    for goal in all_goals:
        pid = str(goal.get("player_id"))
        pname = goal.get("player_name")
        if pid and pname:
            player_names_map[pid] = pname

    player_rankings = []
    for player_id, goals in player_goals.items():
        if goals == 0:
            continue
        player_info = players_map.get(player_id)
        if not player_info:
            continue

        team_id = player_info["team_id"]
        games_played = team_games.get(team_id, 0)

        # Only include players from teams with at least 1 game
        if games_played == 0:
            continue

        player_rankings.append(
            {
                "player_id": player_id,
                "player_name": player_names_map.get(player_id, ""),
                "team_name": player_info["team_name"],
                "goals": goals,
                "games": games_played,
                "team_id": team_id,
                "group_position": team_group_positions.get(team_id, float("inf")),
            }
        )

    player_rankings.sort(
        key=lambda x: (
            -x["goals"],
            x["games"],
            -x["group_position"],
        )
    )

    # Identify tie groups for Best Scorer
    bs_groups = []
    i = 0
    while i < len(player_rankings[:5]):
        group_start = i
        group_size = 1
        for j in range(i + 1, min(i + 5, len(player_rankings))):
            if (
                player_rankings[j]["goals"] == player_rankings[i]["goals"]
                and player_rankings[j]["games"] == player_rankings[i]["games"]
                and player_rankings[j]["group_position"]
                == player_rankings[i]["group_position"]
            ):
                group_size += 1
            else:
                break
        bs_groups.append({"start": group_start, "size": group_size})
        i += group_size

    best_scorer_list = []
    for idx, p in enumerate(player_rankings[:5]):
        position = 1
        for g in bs_groups:
            if idx >= g["start"] and idx < g["start"] + g["size"]:
                for prev_g in bs_groups:
                    if prev_g["start"] < g["start"]:
                        position += prev_g["size"]
                break

        best_scorer_list.append(
            BestScorerResult(
                position=position,
                player_id=p["player_id"],
                team_id=p["team_id"],
                player_name=p["player_name"],
                team_name=p["team_name"],
                goals=p["goals"],
                games=p["games"],
                group_position=p["group_position"],
            )
        )

    team_rankings = []
    for team_id in team_ids:
        goals_suffered = goals_against_team.get(team_id, 0)
        games_played = team_games.get(team_id, 0)
        team_name = teams_map.get(team_id, {}).get("name", "")

        if not team_name:
            continue

        # Only include teams with at least 1 game
        if games_played == 0:
            continue

        team_rankings.append(
            {
                "team_id": team_id,
                "team_name": team_name,
                "goals_suffered": goals_suffered,
                "games": games_played,
                "group_position": team_group_positions.get(team_id, float("inf")),
            }
        )

    team_rankings.sort(
        key=lambda x: (
            x["goals_suffered"],
            -x["games"],
            -x["group_position"],
        )
    )

    # Identify tie groups for Best Defense
    bd_groups = []
    i = 0
    while i < len(team_rankings[:5]):
        group_start = i
        group_size = 1
        for j in range(i + 1, min(i + 5, len(team_rankings))):
            if (
                team_rankings[j]["goals_suffered"] == team_rankings[i]["goals_suffered"]
                and team_rankings[j]["games"] == team_rankings[i]["games"]
                and team_rankings[j]["group_position"]
                == team_rankings[i]["group_position"]
            ):
                group_size += 1
            else:
                break
        bd_groups.append({"start": group_start, "size": group_size})
        i += group_size

    best_defense_list = []
    for idx, t in enumerate(team_rankings[:5]):
        position = 1
        for g in bd_groups:
            if idx >= g["start"] and idx < g["start"] + g["size"]:
                for prev_g in bd_groups:
                    if prev_g["start"] < g["start"]:
                        position += prev_g["size"]
                break

        best_defense_list.append(
            BestDefenseResult(
                position=position,
                team_id=t["team_id"],
                team_name=t["team_name"],
                goals_suffered=t["goals_suffered"],
                games=t["games"],
                group_position=t["group_position"],
            )
        )

    team_cards = {t: 0 for t in team_ids}
    all_cards = (
        await db.db[CARDS_COLLECTION]
        .find({"tournament": ObjectId(tournament_id)})
        .to_list(10000)
    )

    for card in all_cards:
        team_id = str(card.get("team_id"))
        if team_id in team_ids:
            team_cards[team_id] += 1

    fair_play_rankings = []
    for team_id in team_ids:
        cards = team_cards.get(team_id, 0)
        games_played = team_games.get(team_id, 0)
        team_name = teams_map.get(team_id, {}).get("name", "")

        if not team_name:
            continue

        # Only include teams with at least 1 game
        if games_played == 0:
            continue

        fair_play_rankings.append(
            {
                "team_id": team_id,
                "team_name": team_name,
                "cards": cards,
                "games": games_played,
            }
        )

    fair_play_rankings.sort(
        key=lambda x: (
            x["cards"],
            -x["games"],
        )
    )

    # Identify tie groups for Fair Play
    fp_groups = []
    i = 0
    while i < len(fair_play_rankings[:5]):
        group_start = i
        group_size = 1
        for j in range(i + 1, min(i + 5, len(fair_play_rankings))):
            if (
                fair_play_rankings[j]["cards"] == fair_play_rankings[i]["cards"]
                and fair_play_rankings[j]["games"] == fair_play_rankings[i]["games"]
            ):
                group_size += 1
            else:
                break
        fp_groups.append({"start": group_start, "size": group_size})
        i += group_size

    fair_play_list = []
    for idx, t in enumerate(fair_play_rankings[:5]):
        position = 1
        for g in fp_groups:
            if idx >= g["start"] and idx < g["start"] + g["size"]:
                for prev_g in fp_groups:
                    if prev_g["start"] < g["start"]:
                        position += prev_g["size"]
                break

        fair_play_list.append(
            FairPlayResult(
                position=position,
                team_id=t["team_id"],
                team_name=t["team_name"],
                cards=t["cards"],
                games=t["games"],
            )
        )

    logger.info(f"Prizes calculated for tournament '{tournament['name']}'")
    return PrizesResult(
        best_scorer=best_scorer_list,
        best_defense=best_defense_list,
        fair_play=fair_play_list,
    )
