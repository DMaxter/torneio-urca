use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::entity::{Gender, Team};

#[derive(Debug, Deserialize, ToSchema)]
pub(crate) struct CreateTeamDto {
    pub tournament: String,
    pub name: String,
    pub gender: Gender,
    pub responsible: String,
    pub main_coach: String,
    pub assistant_coach: Option<String>,
    pub players: Vec<String>,
    pub physiotherapist: String,
    pub first_deputy: String,
    pub second_deputy: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct TeamDto {
    pub id: String,
    pub tournament: String,
    pub name: String,
    pub gender: Gender,
    pub responsible: String,
    pub main_coach: String,
    pub assistant_coach: Option<String>,
    pub players: Vec<String>,
    pub physiotherapist: String,
    pub first_deputy: String,
    pub second_deputy: Option<String>,
}

impl From<Team> for TeamDto {
    fn from(value: Team) -> Self {
        TeamDto {
            id: value.id.unwrap().to_hex(),
            tournament: value.tournament.to_hex(),
            name: value.name,
            gender: value.gender,
            responsible: value.responsible.to_hex(),
            main_coach: value.main_coach.to_hex(),
            assistant_coach: value.assistant_coach.map(|id| id.to_hex()),
            players: value.players.iter().map(|id| id.to_hex()).collect(),
            physiotherapist: value.physiotherapist.to_hex(),
            first_deputy: value.first_deputy.to_hex(),
            second_deputy: value.second_deputy.map(|id| id.to_hex()),
        }
    }
}
