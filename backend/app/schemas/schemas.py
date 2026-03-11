from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

from app.models.models import Gender, Role, GameStatus, CardType


class CreateUserDto(BaseModel):
    name: str
    gender: Gender
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    roles: List[Role]


class UserDto(BaseModel):
    id: str
    name: str
    gender: Gender
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    confirmed: bool
    roles: List[Role]


class CreateTeamDto(BaseModel):
    tournament: str
    name: str
    gender: Gender
    responsible: str
    main_coach: str
    assistant_coach: Optional[str] = None
    players: List[str]
    physiotherapist: str
    first_deputy: str
    second_deputy: Optional[str] = None


class TeamDto(BaseModel):
    id: str
    tournament: str
    name: str
    gender: Gender
    responsible: str
    main_coach: str
    assistant_coach: Optional[str] = None
    players: List[str]
    physiotherapist: str
    first_deputy: str
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


class CreateGameDto(BaseModel):
    tournament: str
    scheduled_date: datetime
    home_call: CreateGameCallDto
    away_call: CreateGameCallDto


class GameCallDto(BaseModel):
    id: str
    game: str
    team: str
    players: List[str]
    deputy: Optional[str] = None


class GameEventDto(BaseModel):
    pass


class GameDto(BaseModel):
    id: str
    scheduled_date: datetime
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    status: GameStatus
    home_call: GameCallDto
    away_call: GameCallDto
    events: List[Any] = []


class CreateGroupDto(BaseModel):
    tournament: str
    name: str
    teams: List[str]


class GroupDto(BaseModel):
    id: str
    tournament: str
    name: str
    teams: List[str]


class AssignGoalDto(BaseModel):
    tournament: str
    game: str
    team: str
    player: str
    minute: int


class AssignCardDto(BaseModel):
    tournament: str
    game: str
    team: str
    player: str
    card: CardType
    minute: int
