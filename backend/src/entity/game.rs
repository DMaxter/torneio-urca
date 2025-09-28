use std::str::FromStr;

use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::{entity::GameEvent, game::CreateGameDto};

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub(crate) struct Game {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub tournament: ObjectId,
    pub scheduled_date: DateTime<Utc>,
    pub start_date: Option<DateTime<Utc>>,
    pub finish_date: Option<DateTime<Utc>>,
    pub status: GameStatus,
    pub home_call: Option<ObjectId>,
    pub away_call: Option<ObjectId>,
    pub current_period: u8,
    pub events: Vec<GameEvent>,
}

impl From<CreateGameDto> for Game {
    fn from(value: CreateGameDto) -> Self {
        Game {
            tournament: ObjectId::from_str(&value.tournament).unwrap(),
            scheduled_date: value.scheduled_date,
            current_period: 0,
            ..Default::default()
        }
    }
}

#[derive(Clone, Debug, Default, Deserialize, PartialEq, Serialize, ToSchema)]
pub(crate) enum GameStatus {
    #[default]
    NotStarted,
    InProgress,
    Finished,
    Canceled,
}
