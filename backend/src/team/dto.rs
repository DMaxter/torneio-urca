use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::entity::Gender;

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct TeamDto {
    pub id: String,
    pub name: String,
    pub gender: Gender,
    pub responsible: String,
    pub main_coach: String,
    pub assistant_coach: Option<String>,
    pub players: Vec<String>, // Max: 14
    pub physiotherapist: Vec<String>,
    pub first_deputy: Option<String>,
    pub second_deputy: Option<String>,
}
