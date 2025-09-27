use serde::Serialize;
use utoipa::ToSchema;

use crate::entity::Tournament;

#[derive(Debug, Serialize, ToSchema)]
pub(crate) struct TournamentDto {
    pub id: String,
    pub name: String,
    pub teams: Vec<String>,
    pub games: Vec<String>,
    pub groups: Vec<String>,
    pub goals: Vec<String>,
    pub cards: Vec<String>,
}

impl From<Tournament> for TournamentDto {
    fn from(value: Tournament) -> Self {
        TournamentDto {
            id: value.id.unwrap().to_hex(),
            name: value.name,
            teams: value.teams.into_iter().map(|id| id.to_hex()).collect(),
            games: value.games.into_iter().map(|id| id.to_hex()).collect(),
            groups: value.groups.into_iter().map(|id| id.to_hex()).collect(),
            goals: value.goals.into_iter().map(|id| id.to_hex()).collect(),
            cards: value.cards.into_iter().map(|id| id.to_hex()).collect(),
        }
    }
}
