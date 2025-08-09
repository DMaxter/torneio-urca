use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::entity::GameEvent;

#[derive(Debug, Deserialize, Serialize)]
pub(crate) struct Game {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub scheduled_date: DateTime<Utc>,
    pub start_date: DateTime<Utc>,
    pub finish_date: DateTime<Utc>,
    pub game_record: ObjectId,
    pub events: Vec<GameEvent>,
}
