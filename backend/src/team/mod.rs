mod dto;

use bson::Document;
pub(crate) use dto::*;

use axum::{Extension, Json, response::IntoResponse};
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use crate::{SharedState, db::TEAMS_COLLECTION, entity::Team, error::Error};

#[utoipa::path(post, path = "/teams", tag="Teams", request_body(content = CreateTeamDto), responses((status = 200, description = "Team registered")))]
#[instrument(skip(state))]
pub(crate) async fn add_team(
    Extension(state): Extension<SharedState>,
    Json(team): Json<CreateTeamDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating team");

    state
        .read()
        .await
        .db
        .collection(TEAMS_COLLECTION)
        .insert_one(Team::try_from(team)?)
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create team: {e}");

            Error::InternalError
        })?;

    event!(Level::INFO, "Successfully created team");

    Ok(())
}

#[utoipa::path(get, path = "/teams", tag="Teams", responses((status = 200, description = "List of registered teams", body = Vec<TeamDto>)))]
#[instrument(skip(state))]
pub(crate) async fn get_teams(
    Extension(state): Extension<SharedState>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Listing all teams");

    let teams = state
        .read()
        .await
        .db
        .collection(TEAMS_COLLECTION)
        .find(Document::new())
        .await
        .unwrap()
        .try_collect::<Vec<Team>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't get all teams: {e}");

            Error::InternalError
        })?
        .into_iter()
        .map(TeamDto::from)
        .collect::<Vec<_>>();

    Ok(Json(teams))
}
