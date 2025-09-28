use serde::Deserialize;
use utoipa::ToSchema;

use crate::entity::CardType;

#[derive(Debug, Deserialize, ToSchema)]
pub(crate) struct AssignCardDto {
    pub tournament: String,
    pub game: String,
    pub player: String,
    pub team: String,
    pub card: CardType,
    pub minute: u8,
}
