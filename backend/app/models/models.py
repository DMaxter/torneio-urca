from enum import Enum
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Gender(str, Enum):
    Male = "Male"
    Female = "Female"


class Role(str, Enum):
    Admin = "Admin"
    Player = "Player"
    Coach = "Coach"
    Physiotherapist = "Physiotherapist"
    GameDeputy = "GameDeputy"
    Timekeeper = "Timekeeper"
    Organizer = "Organizer"


class GameStatus(str, Enum):
    NotStarted = "NotStarted"
    InProgress = "InProgress"
    Finished = "Finished"
    Canceled = "Canceled"


class CardType(str, Enum):
    Yellow = "Yellow"
    Red = "Red"


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    gender: Gender
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    confirmed: bool = False
    roles: List[Role] = []

    class Config:
        populate_by_name = True


class Team(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    name: str
    gender: Gender
    responsible: str
    main_coach: str
    assistant_coach: Optional[str] = None
    players: List[str] = []
    physiotherapist: str
    first_deputy: str
    second_deputy: Optional[str] = None
    valid: bool = False

    class Config:
        populate_by_name = True


class Tournament(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    teams: List[str] = []
    games: List[str] = []
    groups: List[str] = []
    goals: List[Any] = []
    cards: List[Any] = []

    class Config:
        populate_by_name = True


class GameCall(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    game: Optional[str] = None
    team: str
    players: List[str] = []
    deputy: Optional[str] = None

    class Config:
        populate_by_name = True


class GameEvent(BaseModel):
    pass


class Game(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    scheduled_date: datetime
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    status: GameStatus = GameStatus.NotStarted
    home_call: Optional[str] = None
    away_call: Optional[str] = None
    current_period: int = 0
    events: List[Any] = []

    class Config:
        populate_by_name = True


class Group(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    name: str
    teams: List[str] = []

    class Config:
        populate_by_name = True


class Goal(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    team_id: str
    team_name: str = ""
    player_id: str
    player_name: str = ""
    game_id: str
    period: int
    minute: int
    timestamp: datetime

    class Config:
        populate_by_name = True


class Card(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    team_id: str
    team_name: str = ""
    card: CardType
    game_id: str
    player_id: str
    player_name: str = ""
    period: int
    minute: int
    timestamp: datetime

    class Config:
        populate_by_name = True
