from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import db, TOURNAMENTS_COLLECTION, TEAMS_COLLECTION
from app.schemas.schemas import CreateTournamentDto, TournamentDto
from app.utils.auth import get_current_user, require_manage_games
from app.utils import get_logger, sanitize_for_serialization

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


def tournament_to_dto(tournament: dict) -> TournamentDto:
    """
    Map a MongoDB tournament document dictionary to a serialized TournamentDto.

    Args:
        tournament: The raw MongoDB dictionary document.
    Returns:
        Structured TournamentDto model mapping ObjectIds to strings.
    """
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
    """
    Create a new tournament. Initializes the base relations for teams, games, groups,
    goals, and cards to empty lists.

    Returns:
        The newly created tournament represented as a Dto.
    """
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
    """
    Fetch a list of all globally available tournaments in the database.

    Returns:
        A list of mapped TournamentDto objects.
    """
    get_logger().info("Retrieving all tournaments")
    tournaments = await db.db[TOURNAMENTS_COLLECTION].find().to_list(1000)
    get_logger().info(f"Retrieved {len(tournaments)} tournaments")
    return [tournament_to_dto(t) for t in tournaments]


@router.delete("/{tournament_id}", status_code=204)
async def delete_tournament(
    tournament_id: str, current_user=Depends(require_manage_games)
):
    """
    Delete a specific tournament from the database.
    Prevents deletion if any child teams attached to the tournament have players assigned.

    Raises:
        Error.bad_request if teams contain assigned players.
    """
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
    """
    Internally resolve a single tournament dictionary dynamically querying the database.

    Args:
        tournament_id: String MongoDB ObjectId identifier.
    Returns:
        The fetched MongoDB document mapped as a Python dictionary.
    Raises:
        Error.invalid_id if the format is ill-structured.
        Error.not_found if no exact match exists.
    """
    from app.utils.db import get_entity_or_404
    from database import TOURNAMENTS_COLLECTION

    return await get_entity_or_404(TOURNAMENTS_COLLECTION, tournament_id, "Torneio")


# Import required dependencies
from database import (
    GAMES_COLLECTION,
    GROUPS_COLLECTION,
    GAME_CALLS_COLLECTION,
    TEAMS_COLLECTION,
)
from app.models.models import GameStatus, GamePhase
from app.error import Error


@router.get("/{tournament_id}/preview-knockout")
async def preview_knockout(tournament_id: str):
    """
    Preview what teams would fill knockout slots after group phase ends.
    Shows the resolved matchups without making any changes.
    """
    tournament = await get_tournament(tournament_id)

    # Check if all group games are finished or canceled
    group_games = (
        await db.db[GAMES_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
                "phase": GamePhase.Group,
            }
        )
        .to_list(1000)
    )

    if not group_games:
        raise Error.bad_request("Este torneio não tem jogos de grupo")

    # Count pending games (but don't block preview calculation)
    pending = [
        g
        for g in group_games
        if g.get("status") not in [GameStatus.Finished, GameStatus.Canceled]
    ]

    # Get all groups for this tournament
    groups = (
        await db.db[GROUPS_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
            }
        )
        .to_list(100)
    )

    # Calculate standings for each group with tiebreakers
    from app.routes.prizes import calculate_team_standings

    group_standings: dict[str, list] = {}
    for group in groups:
        group_teams = [str(t) for t in group.get("teams", [])]
        if not group_teams:
            continue
        standings = await calculate_team_standings(
            tournament_id, group_teams, group_games, {}, {}
        )
        group_standings[group.get("name", "")] = standings

    # Get knockout games with placeholders
    knockout_games = (
        await db.db[GAMES_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
                "phase": {"$ne": GamePhase.Group},
            }
        )
        .to_list(100)
    )

    # Build preview
    teams_map = {
        str(t["_id"]): t
        for t in await db.db[TEAMS_COLLECTION]
        .find({"_id": {"$in": tournament.get("teams", [])}})
        .to_list(100)
    }

    preview = []
    for kg in knockout_games:
        home_resolved = None
        away_resolved = None

        # Path 1: Check if team already manually assigned via game call
        if kg.get("home_call"):
            home_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": kg.get("home_call")}
            )
            if home_call and home_call.get("team"):
                team_id = str(home_call.get("team"))
                team = teams_map.get(team_id)
                if team:
                    home_resolved = team.get("name")

        # Path 2: If no team resolved yet, try automatic resolution from group standings
        # This runs regardless of whether home_call exists (handles null team case)
        if (
            not home_resolved
            and kg.get("home_group_ref")
            and kg.get("home_group_position")
        ):
            group_ref = str(kg.get("home_group_ref"))
            position = kg.get("home_group_position")

            get_logger().info(
                f"[DEBUG] Path 2 - group_ref: {group_ref}, position: {position}"
            )
            get_logger().info(f"[DEBUG] total group_games: {len(group_games)}")

            # Filter games belonging to this specific group
            group_games_filtered = [
                g for g in group_games if str(g.get("group")) == group_ref
            ]

            get_logger().info(f"[DEBUG] filtered games: {len(group_games_filtered)}")

            if group_games_filtered:
                get_logger().info(
                    f"[DEBUG] status values: {[g.get('status') for g in group_games_filtered]}"
                )

                # Find standings for this group
                for group in groups:
                    if str(group.get("_id")) == group_ref:
                        group_teams = [str(t) for t in group.get("teams", [])]
                        get_logger().info(f"[DEBUG] group_teams: {group_teams}")
                        if group_teams:
                            standings = await calculate_team_standings(
                                tournament_id,
                                group_teams,
                                group_games,
                                {},
                                teams_map,
                            )
                            if position <= len(standings):
                                team = standings[position - 1]
                                home_resolved = team.get("team_name")
                        break

                        # Away team - same logic
                        # Path 1: Check if team already manually assigned via game call
                        break

        # Check if away team already resolved via game call
        if kg.get("away_call"):
            away_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": kg.get("away_call")}
            )
            if away_call and away_call.get("team"):
                team_id = str(away_call.get("team"))
                team = teams_map.get(team_id)
                if team:
                    away_resolved = team.get("name")

        # Path 2: If no team resolved yet, try automatic resolution from group standings
        if (
            not away_resolved
            and kg.get("away_group_ref")
            and kg.get("away_group_position")
        ):
            group_ref = str(kg.get("away_group_ref"))
            position = kg.get("away_group_position")

            # Filter games belonging to this specific group
            group_games_filtered = [
                g for g in group_games if str(g.get("group")) == group_ref
            ]

            # Calculate standings even before all games finish
            if group_games_filtered:
                for group in groups:
                    if str(group.get("_id")) == group_ref:
                        group_teams = [str(t) for t in group.get("teams", [])]
                        if group_teams:
                            standings = await calculate_team_standings(
                                tournament_id,
                                group_teams,
                                group_games,
                                {},
                                teams_map,
                            )
                            if position <= len(standings):
                                team = standings[position - 1]
                                away_resolved = team.get("team_name")
                        break

        preview.append(
            {
                "game_id": str(kg["_id"]),
                "label": kg.get("label"),
                "phase": kg.get("phase"),
                "home_placeholder": kg.get("home_placeholder"),
                "away_placeholder": kg.get("away_placeholder"),
                "home_resolved": home_resolved,
                "away_resolved": away_resolved,
            }
        )

    # Check if teams already assigned to knockout games (meaning already advanced)
    can_advance = False
    if knockout_games and len(pending) == 0:
        # Check if knockout games already have teams assigned via game calls
        has_teams_assigned = False
        for kg in knockout_games:
            home_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": kg.get("home_call")}
            )
            away_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"_id": kg.get("away_call")}
            )
            if (
                home_call
                and away_call
                and home_call.get("team")
                and away_call.get("team")
            ):
                has_teams_assigned = True
                break
        can_advance = not has_teams_assigned

    return {
        "complete": len(pending) == 0,
        "remaining": len(pending),
        "knockout": preview,
        "canAdvance": can_advance,
    }


@router.post("/{tournament_id}/advance-phase")
async def advance_to_knockout(
    tournament_id: str, current_user=Depends(require_manage_games)
):
    """
    Advance from group phase to knockout phase.
    Resolves team placeholders with actual teams based on group standings.
    """
    tournament = await get_tournament(tournament_id)

    # Check if all group games are finished or canceled
    group_games = (
        await db.db[GAMES_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
                "phase": GamePhase.Group,
            }
        )
        .to_list(1000)
    )

    if not group_games:
        raise Error.bad_request("Este torneio não tem jogos de grupo")

    pending = [
        g
        for g in group_games
        if g.get("status") not in [GameStatus.Finished, GameStatus.Canceled]
    ]

    if pending:
        raise Error.bad_request(
            f"Ainda faltam {len(pending)} jogo(s) de grupo. Não é possível avançar para a fase de eliminatórias."
        )

    # Calculate group standings
    groups = (
        await db.db[GROUPS_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
            }
        )
        .to_list(100)
    )

    from app.routes.prizes import calculate_team_standings

    # Load teams for this tournament (needed for calculate_team_standings)
    teams = (
        await db.db[TEAMS_COLLECTION]
        .find({"_id": {"$in": tournament.get("teams", [])}})
        .to_list(100)
    )
    teams_map = {str(t["_id"]): t for t in teams}

    group_standings: dict[str, list] = {}
    for group in groups:
        group_teams = [str(t) for t in group.get("teams", [])]
        if not group_teams:
            continue
        standings = await calculate_team_standings(
            tournament_id, group_teams, group_games, {}, teams_map
        )
        group_standings[group.get("name", "")] = standings

    # Get knockout games
    knockout_games = (
        await db.db[GAMES_COLLECTION]
        .find(
            {
                "tournament": ObjectId(tournament_id),
                "phase": {"$ne": GamePhase.Group},
            }
        )
        .to_list(100)
    )

    # Resolve and update each knockout game using structured refs
    updated = []
    for kg in knockout_games:
        home_team_id = None
        away_team_id = None

        # Calculate from group standings
        if kg.get("home_group_ref") and kg.get("home_group_position"):
            group_ref = str(kg.get("home_group_ref"))
            position = kg.get("home_group_position")
            for group in groups:
                if str(group.get("_id")) == group_ref:
                    group_teams = [str(t) for t in group.get("teams", [])]
                    if group_teams:
                        standings = await calculate_team_standings(
                            tournament_id, group_teams, group_games, {}, teams_map
                        )
                        if position <= len(standings):
                            team_id = standings[position - 1].get("team_id")
                            if team_id:
                                home_team_id = ObjectId(team_id)
                    break

        if kg.get("away_group_ref") and kg.get("away_group_position"):
            group_ref = str(kg.get("away_group_ref"))
            position = kg.get("away_group_position")
            for group in groups:
                if str(group.get("_id")) == group_ref:
                    group_teams = [str(t) for t in group.get("teams", [])]
                    if group_teams:
                        standings = await calculate_team_standings(
                            tournament_id, group_teams, group_games, {}, teams_map
                        )
                        if position <= len(standings):
                            team_id = standings[position - 1].get("team_id")
                            if team_id:
                                away_team_id = ObjectId(team_id)
                    break

        # Create or update game calls (same as group games)
        if home_team_id and away_team_id:
            # Check if game calls already exist
            existing_home_call = await db.db[GAME_CALLS_COLLECTION].find_one(
                {"game": kg["_id"]}
            )
            existing_away_calls = (
                await db.db[GAME_CALLS_COLLECTION].find({"game": kg["_id"]}).to_list(2)
            )
            existing_away_call = (
                existing_away_calls[1] if len(existing_away_calls) > 1 else None
            )

            if existing_home_call and existing_away_call:
                # Fetch players from team and update game calls with both team and players
                home_team_obj = await db.db[TEAMS_COLLECTION].find_one(
                    {"_id": home_team_id}
                )
                home_players = (
                    [
                        {"player": p, "number": None}
                        for p in home_team_obj.get("players", [])
                    ]
                    if home_team_obj
                    else []
                )

                away_team_obj = await db.db[TEAMS_COLLECTION].find_one(
                    {"_id": away_team_id}
                )
                away_players = (
                    [
                        {"player": p, "number": None}
                        for p in away_team_obj.get("players", [])
                    ]
                    if away_team_obj
                    else []
                )

                await db.db[GAME_CALLS_COLLECTION].update_one(
                    {"_id": existing_home_call["_id"]},
                    {"$set": {"team": home_team_id, "players": home_players}},
                )
                await db.db[GAME_CALLS_COLLECTION].update_one(
                    {"_id": existing_away_call["_id"]},
                    {"$set": {"team": away_team_id, "players": away_players}},
                )
            else:
                # Create new game calls (same as group game creation)
                home_team = await db.db["teams"].find_one({"_id": home_team_id})
                away_team = await db.db["teams"].find_one({"_id": away_team_id})

                home_players = (
                    [
                        {"player": p, "number": None}
                        for p in home_team.get("players", [])
                    ]
                    if home_team
                    else []
                )
                away_players = (
                    [
                        {"player": p, "number": None}
                        for p in away_team.get("players", [])
                    ]
                    if away_team
                    else []
                )

                home_call_id = await db.db[GAME_CALLS_COLLECTION].insert_one(
                    {
                        "team": home_team_id,
                        "players": home_players,
                        "staff": [],
                        "deputy": None,
                        "game": kg["_id"],
                    }
                )
                away_call_id = await db.db[GAME_CALLS_COLLECTION].insert_one(
                    {
                        "team": away_team_id,
                        "players": away_players,
                        "staff": [],
                        "deputy": None,
                        "game": kg["_id"],
                    }
                )

                # Link game calls to game
                await db.db[GAMES_COLLECTION].update_one(
                    {"_id": kg["_id"]},
                    {
                        "$set": {
                            "home_call": home_call_id.inserted_id,
                            "away_call": away_call_id.inserted_id,
                        }
                    },
                )

            updated.append(kg.get("label", str(kg["_id"])))

    get_logger().info(
        f"[{current_user['username']}] Advanced tournament '{tournament_id}' to knockout phase"
    )

    return {
        "success": True,
        "updated_games": len(updated),
        "games": updated,
    }
