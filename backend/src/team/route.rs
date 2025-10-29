use axum::{Extension, Json, response::IntoResponse};
use bson::{Document, doc};
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use crate::{
    SharedState,
    db::{TEAMS_COLLECTION, TOURNAMENTS_COLLECTION},
    entity::{Team, Tournament},
    error::Error,
    team::{CreateTeamDto, TeamDto},
    tournament::get_tournament,
};

#[utoipa::path(post, path = "/teams", tag="Teams", request_body(content = CreateTeamDto), responses((status = 200, description = "Team registered")))]
#[instrument(skip(state))]
pub(crate) async fn add_team(
    Extension(state): Extension<SharedState>,
    Json(team): Json<CreateTeamDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating team");

    let db = &state.read().await.db;

    let tournament = get_tournament(db, &team.tournament).await?.id.unwrap();
    let mut entity = Team::try_from(team)?;
    let team_id = db
        .collection(TEAMS_COLLECTION)
        .insert_one(entity.clone())
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create team: {e}");

            Error::Internal
        })?
        .inserted_id
        .as_object_id()
        .unwrap();

    db.collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .update_one(
            doc! { "_id": &tournament },
            doc! { "$push": { "teams": &team_id } },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add team to tournament: {e}");

            Error::Internal
        })?;

    entity.id = Some(team_id);

    event!(Level::INFO, "Successfully created team");

    Ok(Json(TeamDto::from(entity)))
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

            Error::Internal
        })?
        .into_iter()
        .map(TeamDto::from)
        .collect::<Vec<_>>();

    Ok(Json(teams))
}
