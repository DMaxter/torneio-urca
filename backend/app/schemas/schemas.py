from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

from app.models.models import GameStatus, GamePhase, CardType, StaffType
from app.constants import TournamentPhase


class CreateUserDto(BaseModel):
    username: str
    password: str


class UserRoles:
    MANAGE_PLAYERS = "manage_players"
    MANAGE_GAMES = "manage_games"
    MANAGE_GAME_EVENTS = "manage_game_events"
    FILL_GAME_CALLS = "fill_game_calls"
    OPEN_CALENDAR = "open_calendar"
    ANNOUNCER = "announcer"

    ALL = [
        MANAGE_PLAYERS,
        MANAGE_GAMES,
        MANAGE_GAME_EVENTS,
        FILL_GAME_CALLS,
        OPEN_CALENDAR,
        ANNOUNCER,
    ]


class AssignUserGamesForCallsDto(BaseModel):
    assigned_games_for_calls: List[str] = []


class UserDto(BaseModel):
    id: str
    username: str
    roles: List[str] = []
    assigned_games: List[str] = []
    assigned_games_for_calls: List[str] = []


class UpdateUserRolesDto(BaseModel):
    roles: List[str] = []


class AssignUserGamesDto(BaseModel):
    assigned_games: List[str] = []


class ChangePasswordDto(BaseModel):
    current_password: str
    new_password: str


class CreatePlayerDto(BaseModel):
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    is_federated: bool = False
    federation_team: Optional[str] = None
    federation_exams_up_to_date: bool = False
    is_goalkeeper: bool = False


class CreateAnnouncementDto(BaseModel):
    title: str
    content: str
    is_active: bool = True


class UpdateAnnouncementDto(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class AnnouncementDto(BaseModel):
    id: str
    title: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PlayerDto(BaseModel):
    id: str
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    citizen_card_file_id: Optional[str] = None
    proof_of_residency_file_id: Optional[str] = None
    authorization_file_id: Optional[str] = None
    is_federated: bool
    federation_team: Optional[str] = None
    federation_exams_up_to_date: bool
    is_confirmed: bool
    team: Optional[str] = None
    is_goalkeeper: bool = False


class CreateStaffDto(BaseModel):
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    staff_type: StaffType


class StaffDto(BaseModel):
    id: str
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    staff_type: StaffType
    citizen_card_file_id: Optional[str] = None
    authorization_file_id: Optional[str] = None
    team_name: Optional[str] = None


class CreateTeamDto(BaseModel):
    tournament: str
    name: str
    responsible_name: str
    responsible_email: str
    responsible_phone: str
    main_coach: Optional[str] = None
    assistant_coach: Optional[str] = None
    players: List[str]
    physiotherapist: Optional[str] = None
    first_deputy: Optional[str] = None
    second_deputy: Optional[str] = None


class TeamDto(BaseModel):
    id: str
    tournament: str
    name: str
    responsible_name: str
    responsible_email: str
    responsible_phone: str
    main_coach: Optional[str] = None
    assistant_coach: Optional[str] = None
    players: List[str]
    physiotherapist: Optional[str] = None
    first_deputy: Optional[str] = None
    second_deputy: Optional[str] = None
    cancel_token: Optional[str] = None


class TournamentDto(BaseModel):
    id: str
    name: str
    teams: List[str]
    games: List[str]
    groups: List[str]
    goals: List[Any]
    cards: List[Any]
    phase: TournamentPhase = TournamentPhase.GROUP


class CreateTournamentDto(BaseModel):
    name: str
    phase: TournamentPhase = TournamentPhase.GROUP


class UpdateTournamentDto(BaseModel):
    name: str


class CreateGameCallDto(BaseModel):
    team: str


class UpdateGameCallDto(BaseModel):
    players: List[dict]  # [{"player": str, "number": int | None}]
    staff: Optional[List[str]] = None


class ConfirmGameCallDto(BaseModel):
    confirmed: bool


class CreateGameDto(BaseModel):
    tournament: str
    label: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    home_call: Optional[CreateGameCallDto] = None
    away_call: Optional[CreateGameCallDto] = None
    phase: GamePhase = GamePhase.Group
    home_placeholder: Optional[str] = None
    away_placeholder: Optional[str] = None
    # Group reference for group phase games
    group: Optional[str] = None
    # Structured group reference for knockout
    home_group_ref: Optional[str] = None
    home_group_position: Optional[int] = None
    away_group_ref: Optional[str] = None
    away_group_position: Optional[int] = None
    next_game_winner: Optional[str] = None
    next_game_loser: Optional[str] = None


class GameCallDto(BaseModel):
    id: str
    game: str
    team: str | None = None
    players: List[dict]  # [{"player": str, "number": int | None}]
    staff: List[str] = []
    deputy: Optional[str] = None


class GameEventDto(BaseModel):
    pass


class GameDto(BaseModel):
    id: str
    tournament: str
    label: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    status: GameStatus
    phase: GamePhase = GamePhase.Group
    home_placeholder: Optional[str] = None
    away_placeholder: Optional[str] = None
    group: Optional[str] = None
    home_group_ref: Optional[str] = None
    home_group_position: Optional[int] = None
    away_group_ref: Optional[str] = None
    away_group_position: Optional[int] = None
    home_call: Optional[GameCallDto] = None
    away_call: Optional[GameCallDto] = None
    events: List[Any] = []
    current_period: int = 0
    period_elapsed_seconds: int = 0
    timer_active: bool = False
    timer_started_at: Optional[datetime] = None
    next_game_winner: Optional[str] = None
    next_game_loser: Optional[str] = None


class CreateGroupDto(BaseModel):
    tournament: str
    name: str
    teams: List[str]


class GroupDto(BaseModel):
    id: str
    tournament: str
    name: str
    teams: List[str]


class UpdateGameDto(BaseModel):
    scheduled_date: Optional[datetime] = None


class UpdateGameStatusDto(BaseModel):
    status: GameStatus


class UpdatePeriodDto(BaseModel):
    action: str  # "start_new", "resume", "stop", "end", "set_seconds"
    period: Optional[int] = None
    seconds: Optional[int] = None


class CreateGameDayDto(BaseModel):
    tournament: str
    date: str
    num_games: int
    start_time: str


class GameDayDto(BaseModel):
    id: str
    tournament: str
    date: str
    num_games: int
    start_time: str


class AssignGoalDto(BaseModel):
    tournament: str
    game: str
    team: str  # Scoring team
    player_number: Optional[int] = None  # Shirt number from game call
    own_goal: bool = False  # If true, player is from opposing team
    minute: int
    second: Optional[int] = None


class AssignCardDto(BaseModel):
    tournament: str
    game: str
    team: str
    player_number: Optional[int] = None  # Shirt number from game call
    staff_id: Optional[str] = None  # For staff (optional)
    card: CardType
    minute: int
    second: Optional[int] = None
    is_direct_free_kick: bool = False


class AssignFoulDto(BaseModel):
    tournament: str
    game: str
    team: str
    player_number: Optional[int] = None  # Shirt number from game call
    staff_id: Optional[str] = None  # For staff (optional)
    minute: int
    second: Optional[int] = None
    is_direct_free_kick: bool = False


class ManualEventDto(BaseModel):
    description: str


class AssignPenaltyDto(BaseModel):
    tournament: str
    game: str
    team: str
    player_number: int
    scored: bool
    minute: int
    second: Optional[int] = None


class CreateAdminPlayerDto(BaseModel):
    name: str
    birth_date: datetime
    team: str
    tournament: str
    is_federated: bool = False
    federation_team: Optional[str] = None
    fiscal_number: Optional[str] = None


class RegisterTeamStartDto(BaseModel):
    tournament: str
    name: str
    responsible_name: str
    responsible_email: str
    responsible_phone: str


class RegisterTeamCompleteDto(BaseModel):
    team_id: str


class RegisterStaffDto(BaseModel):
    team_id: str
    staff_type: StaffType
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str


class RegisterPlayerDto(BaseModel):
    team_id: str
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    is_federated: bool = False
    federation_team: Optional[str] = None
    federation_exams_up_to_date: bool = False
