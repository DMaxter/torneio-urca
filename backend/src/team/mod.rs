mod dto;

pub(crate) use dto::*;

use axum::{Extension, Json, response::IntoResponse};

use crate::{SharedState, error::Error};

pub(crate) async fn add_team(
    Extension(state): Extension<SharedState>,
    Json(team): Json<TeamDto>,
) -> Result<impl IntoResponse, Error> {
    Ok(())
}
