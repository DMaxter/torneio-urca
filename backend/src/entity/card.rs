use std::str::FromStr;

use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_with::serde_as;
use utoipa::ToSchema;

use crate::card::AssignCardDto;

#[serde_as]
#[derive(Debug, Default, Deserialize, Serialize)]
pub(crate) struct Card {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub tournament: ObjectId,
    pub team_id: ObjectId,
    pub team_name: String,
    pub card: CardType,
    pub game_id: ObjectId,
    pub player_id: ObjectId,
    pub player_name: String,
    pub period: u8,
    pub minute: u8,
    #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
    pub timestamp: DateTime<Utc>,
}

#[derive(Clone, Debug, Default, Deserialize, Serialize, ToSchema)]
pub(crate) enum CardType {
    #[default]
    Yellow,
    Red,
}

impl From<AssignCardDto> for Card {
    fn from(value: AssignCardDto) -> Self {
        Card {
            tournament: ObjectId::from_str(&value.tournament).unwrap(),
            team_id: ObjectId::from_str(&value.team).unwrap(),
            player_id: ObjectId::from_str(&value.player).unwrap(),
            game_id: ObjectId::from_str(&value.game).unwrap(),
            card: value.card,
            timestamp: Utc::now(),
            ..Default::default()
        }
    }
}
