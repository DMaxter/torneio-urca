use serde::Deserialize;
use utoipa::ToSchema;

#[derive(Debug, Deserialize, ToSchema)]
pub(crate) struct AssignGoalDto {
    pub tournament: String,
    pub game: String,
    pub team: String,
    pub player: String,
    pub minute: u8,
}
