use std::str::FromStr;

use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_with::serde_as;

use crate::goal::AssignGoalDto;

#[serde_as]
#[derive(Debug, Default, Deserialize, Serialize)]
pub(crate) struct Goal {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub tournament: ObjectId,
    pub team_id: ObjectId,
    pub team_name: String,
    pub player_id: ObjectId,
    pub player_name: String,
    pub game_id: ObjectId,
    pub period: u8,
    pub minute: u8,
    #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
    pub timestamp: DateTime<Utc>,
}

impl From<AssignGoalDto> for Goal {
    fn from(value: AssignGoalDto) -> Self {
        Goal {
            tournament: ObjectId::from_str(&value.tournament).unwrap(),
            team_id: ObjectId::from_str(&value.team).unwrap(),
            player_id: ObjectId::from_str(&value.player).unwrap(),
            game_id: ObjectId::from_str(&value.game).unwrap(),
            minute: value.minute,
            timestamp: Utc::now(),
            ..Default::default()
        }
    }
}
