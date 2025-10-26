use axum::{Extension, Json, response::IntoResponse};
use bson::Document;
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use crate::{
    SharedState,
    db::TOURNAMENTS_COLLECTION,
    entity::Tournament,
    error::Error,
    tournament::{CreateTournamentDto, TournamentDto},
};

#[utoipa::path(post, path = "/tournaments", tag = "Tournaments", request_body = String, responses((status = 200, description = "Tournament created")))]
#[instrument(skip(state))]
pub(crate) async fn add_tournament(
    Extension(state): Extension<SharedState>,
    Json(tournament): Json<CreateTournamentDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating tournament");

    let id = state
        .read()
        .await
        .db
        .collection(TOURNAMENTS_COLLECTION)
        .insert_one(Tournament {
            name: tournament.name.clone(),
            ..Default::default()
        })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create tournament: {e}");

            Error::Internal
        })?
        .inserted_id
        .as_object_id()
        .unwrap()
        .to_hex();

    event!(Level::INFO, "Successfully created tournament");

    Ok(Json(TournamentDto {
        id,
        name: tournament.name,
        ..Default::default()
    }))
}

#[utoipa::path(get, path = "/tournaments", tag = "Tournaments", responses((status = 200, description = "List of tournaments", body = Vec<TournamentDto>)))]
#[instrument(skip(state))]
pub(crate) async fn get_tournaments(
    Extension(state): Extension<SharedState>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Listing all tournaments");

    let tournaments = state
        .read()
        .await
        .db
        .collection(TOURNAMENTS_COLLECTION)
        .find(Document::new())
        .await
        .unwrap()
        .try_collect::<Vec<Tournament>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't get all tournaments: {e}");

            Error::Internal
        })?
        .into_iter()
        .map(TournamentDto::from)
        .collect::<Vec<_>>();

    Ok(Json(tournaments))
}
