use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub(crate) struct Card {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub team_id: ObjectId,
    pub team_name: String,
    pub card: CardType,
    pub player_id: ObjectId,
    pub player_name: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub(crate) enum CardType {
    Yellow,
    Red,
}
