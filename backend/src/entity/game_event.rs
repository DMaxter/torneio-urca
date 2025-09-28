use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_with::serde_as;

use crate::entity::{Card, CardType};

#[serde_as]
#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) enum GameEvent {
    StartTime {
        period: u8,
        #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
        timestamp: DateTime<Utc>,
    },
    Foul {
        player_id: ObjectId,
        player_name: String,
        team_name: String,
        period: u8,
        minute: u8,
        card: CardType,
        #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
        timestamp: DateTime<Utc>,
    },
    EndTime {
        period: u8,
        #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
        timestamp: DateTime<Utc>,
    },
    Goal {
        player_id: ObjectId,
        player_name: String,
        period: u8,
        minute: u8,
        #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
        timestamp: DateTime<Utc>,
    },
    Break {
        team_id: ObjectId,
        team_name: String,
        #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
        timestamp: DateTime<Utc>,
    },
    Resume {
        #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
        timestamp: DateTime<Utc>,
    },
}

impl From<Card> for GameEvent {
    fn from(value: Card) -> Self {
        GameEvent::Foul {
            player_id: value.player_id,
            player_name: value.player_name,
            team_name: value.team_name,
            period: value.period,
            minute: value.minute,
            card: value.card,
            timestamp: value.timestamp,
        }
    }
}
