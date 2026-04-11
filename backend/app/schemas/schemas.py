from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

from app.models.models import GameStatus, GamePhase, CardType, StaffType


class CreateUserDto(BaseModel):
    username: str
    password: str


class UserRoles:
    MANAGE_PLAYERS = "manage_players"
    MANAGE_GAMES = "manage_games"
    MANAGE_GAME_EVENTS = "manage_game_events"
    FILL_GAME_CALLS = "fill_game_calls"

    ALL = [MANAGE_PLAYERS, MANAGE_GAMES, MANAGE_GAME_EVENTS, FILL_GAME_CALLS]


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
    proof_of_residency_file_id: Optional[str] = None
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


class TournamentDto(BaseModel):
    id: str
    name: str
    teams: List[str]
    games: List[str]
    groups: List[str]
    goals: List[Any]
    cards: List[Any]


class CreateTournamentDto(BaseModel):
    name: str


class CreateGameCallDto(BaseModel):
    team: str


class UpdateGameCallDto(BaseModel):
    players: List[dict]  # [{"player": str, "number": int | None}]


class ConfirmGameCallDto(BaseModel):
    confirmed: bool


class CreateGameDto(BaseModel):
    tournament: str
    scheduled_date: Optional[datetime] = None
    home_call: Optional[CreateGameCallDto] = None
    away_call: Optional[CreateGameCallDto] = None
    phase: GamePhase = GamePhase.Group
    home_placeholder: Optional[str] = None
    away_placeholder: Optional[str] = None


class GameCallDto(BaseModel):
    id: str
    game: str
    team: str
    players: List[dict]  # [{"player": str, "number": int | None}]
    deputy: Optional[str] = None


class GameEventDto(BaseModel):
    pass


class GameDto(BaseModel):
    id: str
    tournament: str
    scheduled_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    status: GameStatus
    phase: GamePhase = GamePhase.Group
    home_placeholder: Optional[str] = None
    away_placeholder: Optional[str] = None
    home_call: Optional[GameCallDto] = None
    away_call: Optional[GameCallDto] = None
    events: List[Any] = []
    current_period: int = 0
    period_elapsed_seconds: int = 0
    timer_active: bool = False
    timer_started_at: Optional[datetime] = None


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


class AssignCardDto(BaseModel):
    tournament: str
    game: str
    team: str
    player_number: Optional[int] = None  # Shirt number from game call
    staff_id: Optional[str] = None  # For staff (optional)
    card: CardType
    minute: int


class AssignFoulDto(BaseModel):
    tournament: str
    game: str
    team: str
    player_number: Optional[int] = None  # Shirt number from game call
    staff_id: Optional[str] = None  # For staff (optional)
    minute: int


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
