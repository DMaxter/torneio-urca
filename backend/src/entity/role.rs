use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Clone, Debug, Deserialize, PartialEq, Serialize, ToSchema)]
pub(crate) enum Role {
    Admin,
    Player,
    Coach,
    Physiotherapist,
    GameDeputy,
    Timekeeper,
    Organizer,
}
