"""
Domain models for the tournament management system.

These models represent the core entities in the futsal tournament system:
- User: Admin users who manage tournaments
- Player: Individual players registered to teams
- Staff: Team staff members (coaches, physiotherapists, deputies)
- Team: Futsal teams participating in tournaments
- Tournament: The main organizing entity containing teams, games, and groups
- Game: Individual matches between teams
- GameCall: The roster of players called for a specific game
- Group: Groups of teams within a tournament for round-robin play
- Goal/Card: Game events tracking scoring and discipline
"""

from enum import Enum
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class StaffType(str, Enum):
    """Types of staff members that can be associated with a team."""

    Coach = "Coach"
    Physiotherapist = "Physiotherapist"
    GameDeputy = "GameDeputy"


class GameStatus(str, Enum):
    """Status of a game in the tournament lifecycle."""

    NotStarted = "NotStarted"
    InProgress = "InProgress"
    Finished = "Finished"
    Canceled = "Canceled"


class CardType(str, Enum):
    """Types of cards that can be given to players during games."""

    Yellow = "Yellow"
    Red = "Red"


class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    username: str
    password: str


class Player(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    name: str
    birth_date: datetime
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: str
    citizen_card_file_id: Optional[str] = None
    proof_of_residency_file_id: Optional[str] = None
    authorization_file_id: Optional[str] = None
    is_federated: bool = False
    federation_team: Optional[str] = None
    federation_exams_up_to_date: bool = False
    is_confirmed: bool = False


class Staff(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    name: str
    birth_date: Optional[datetime] = None
    address: Optional[str] = None
    place_of_birth: Optional[str] = None
    fiscal_number: Optional[str] = None
    staff_type: StaffType
    citizen_card_file_id: Optional[str] = None
    proof_of_residency_file_id: Optional[str] = None
    authorization_file_id: Optional[str] = None


class Team(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    name: str
    responsible_name: str
    responsible_email: str
    responsible_phone: str
    main_coach: str
    assistant_coach: Optional[str] = None
    players: List[str] = []
    physiotherapist: str
    first_deputy: str
    second_deputy: Optional[str] = None
    valid: bool = False


class Tournament(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    name: str
    teams: List[str] = []
    games: List[str] = []
    groups: List[str] = []
    goals: List[Any] = []
    cards: List[Any] = []


class GameCall(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    game: Optional[str] = None
    team: str
    players: List[
        dict
    ] = []  # [{"player": str, "number": int}] or [{"player": str, "number": None}] for removed
    deputy: Optional[str] = None


class GameEvent(BaseModel):
    pass


class GamePhase(str, Enum):
    Group = "group"
    QuarterFinal = "quarter_final"
    SemiFinal = "semi_final"
    Final = "final"
    ThirdPlace = "third_place"


class Game(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    scheduled_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    status: GameStatus = GameStatus.NotStarted
    home_call: Optional[str] = None
    away_call: Optional[str] = None
    phase: GamePhase = GamePhase.Group
    home_placeholder: Optional[str] = None
    away_placeholder: Optional[str] = None
    current_period: int = 0
    events: List[Any] = []


class Group(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    name: str
    teams: List[str] = []


class GameDay(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    tournament: str
    date: str  # "YYYY-MM-DD"
    num_games: int
    start_time: str  # "HH:MM"


class Goal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

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


class Card(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

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
