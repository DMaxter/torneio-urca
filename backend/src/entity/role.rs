use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub(crate) enum Role {
    Admin,
    Player,
    Coach,
    AssistantCoach,
    Physiotherapist,
    GameDeputy,
    TeamResponsible,
    Timekeeper,
}
