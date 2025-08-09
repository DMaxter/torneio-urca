use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub(crate) struct GameRecord {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub game: ObjectId,
    pub home_team: ObjectId,
    pub away_team: ObjectId,
    pub home_players: Vec<ObjectId>, // Max: 12
    pub away_players: Vec<ObjectId>, // Max: 12
    pub home_deputy: ObjectId,
    pub away_deputy: ObjectId,
}
