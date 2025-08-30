use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) enum GameEvent {
    StartTime {
        period: u8,
        #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
        timestamp: DateTime<Utc>,
    },
    Foul {
        player_id: ObjectId,
        player_name: String,
        team_name: String,
        period: u8,
        minute: u8,
        #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
        timestamp: DateTime<Utc>,
    },
    EndTime {
        period: u8,
        #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
        timestamp: DateTime<Utc>,
    },
    Goal {
        player_id: ObjectId,
        player_name: String,
        period: u8,
        minute: u8,
        #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
        timestamp: DateTime<Utc>,
    },
    Break {
        team_id: ObjectId,
        team_name: String,
        #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
        timestamp: DateTime<Utc>,
    },
    Resume {
        #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
        timestamp: DateTime<Utc>,
    },
}
