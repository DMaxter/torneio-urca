use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};

use crate::entity::Gender;

#[derive(Debug, Deserialize, Serialize)]
pub struct Team {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub name: String,
    pub gender: Gender,
    pub responsible: ObjectId,
    pub main_coach: ObjectId,
    pub assistant_coach: Option<ObjectId>,
    pub players: Vec<ObjectId>, // Max: 14
    pub physiotherapist: Vec<ObjectId>,
    pub first_deputy: Option<ObjectId>,
    pub second_deputy: Option<ObjectId>,
}
