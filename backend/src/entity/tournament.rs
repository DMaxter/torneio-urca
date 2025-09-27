use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};

#[derive(Debug, Default, Deserialize, Serialize)]
pub struct Tournament {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub name: String,
    pub teams: Vec<ObjectId>,
    pub games: Vec<ObjectId>,
    pub groups: Vec<ObjectId>,
    pub goals: Vec<ObjectId>,
    pub cards: Vec<ObjectId>,
}
