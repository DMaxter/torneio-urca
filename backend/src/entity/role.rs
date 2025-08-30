use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub(crate) enum Role {
    Admin,
    Player,
    Coach,
    AssistantCoach,
    Physiotherapist,
    GameDeputy,
    TeamResponsible,
    Timekeeper,
    Organizer,
}
