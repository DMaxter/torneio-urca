use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::entity::{Game, GameCall, GameEvent, GameStatus};

#[derive(Clone, Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct CreateGameDto {
    pub scheduled_date: DateTime<Utc>,
    pub home_call: CreateGameCallDto,
    pub away_call: CreateGameCallDto,
}

#[derive(Clone, Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct CreateGameCallDto {
    pub team: String,
}

#[derive(Debug, Default, Deserialize, Serialize, ToSchema)]
pub(crate) struct GameDto {
    pub id: String,
    pub scheduled_date: DateTime<Utc>,
    pub start_date: Option<DateTime<Utc>>,
    pub finish_date: Option<DateTime<Utc>>,
    pub status: GameStatus,
    pub home_call: GameCallDto,
    pub away_call: GameCallDto,
    pub events: Vec<GameEventDto>,
}

impl From<Game> for GameDto {
    fn from(value: Game) -> Self {
        GameDto {
            id: value.id.unwrap().to_hex(),
            scheduled_date: value.scheduled_date,
            start_date: value.start_date,
            finish_date: value.finish_date,
            status: value.status,
            events: value.events.into_iter().map(GameEventDto::from).collect(),
            ..Default::default()
        }
    }
}

#[derive(Debug, Default, Deserialize, Serialize, ToSchema)]
pub(crate) struct GameCallDto {
    pub id: String,
    pub game: String,
    pub team: String,
    pub players: Vec<String>,
    pub deputy: Option<String>,
}

impl From<GameCall> for GameCallDto {
    fn from(value: GameCall) -> Self {
        GameCallDto {
            id: value.id.unwrap().to_hex(),
            game: value.game.unwrap().to_hex(),
            team: value.team.to_hex(),
            players: value.players.into_iter().map(|p| p.to_hex()).collect(),
            deputy: value.deputy.map(|id| id.to_hex()),
        }
    }
}

#[derive(Clone, Debug, Deserialize, Serialize, ToSchema)]
pub(crate) enum GameEventDto {
    StartTime {
        period: u8,
        timestamp: DateTime<Utc>,
    },
    EndTime {
        period: u8,
        timestamp: DateTime<Utc>,
    },
    Foul {
        player_id: String,
        player_name: String,
        team_name: String,
        period: u8,
        minute: u8,
        timestamp: DateTime<Utc>,
    },
    Goal {
        player_id: String,
        player_name: String,
        period: u8,
        minute: u8,
        timestamp: DateTime<Utc>,
    },
    Break {
        team_id: String,
        team_name: String,
        timestamp: DateTime<Utc>,
    },
    Resume {
        timestamp: DateTime<Utc>,
    },
}

impl From<GameEvent> for GameEventDto {
    fn from(value: GameEvent) -> Self {
        match value {
            GameEvent::StartTime { period, timestamp } => {
                GameEventDto::StartTime { period, timestamp }
            }
            GameEvent::Foul {
                player_id,
                player_name,
                team_name,
                period,
                minute,
                timestamp,
            } => GameEventDto::Foul {
                player_id: player_id.to_hex(),
                player_name,
                team_name,
                period,
                minute,
                timestamp,
            },
            GameEvent::EndTime { period, timestamp } => GameEventDto::EndTime { period, timestamp },
            GameEvent::Goal {
                player_id,
                player_name,
                period,
                minute,
                timestamp,
            } => GameEventDto::Goal {
                player_id: player_id.to_hex(),
                player_name,
                period,
                minute,
                timestamp,
            },
            GameEvent::Break {
                team_id,
                team_name,
                timestamp,
            } => GameEventDto::Break {
                team_id: team_id.to_hex(),
                team_name,
                timestamp,
            },
            GameEvent::Resume { timestamp } => GameEventDto::Resume { timestamp },
        }
    }
}
