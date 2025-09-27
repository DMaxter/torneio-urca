mod dto;

use axum::{Extension, Json, response::IntoResponse};
use bson::{Document, doc};
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use crate::{
    SharedState,
    db::{GROUPS_COLLECTION, TOURNAMENTS_COLLECTION},
    entity::{Group, Tournament},
    error::Error,
};
pub(crate) use dto::*;

#[utoipa::path(post, path = "/groups", tag = "Groups", request_body(content = CreateGroupDto), responses((status = 200, description = "Group registered")))]
#[instrument(skip(state))]
pub(crate) async fn add_group(
    Extension(state): Extension<SharedState>,
    Json(group): Json<CreateGroupDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating group");

    let db = &state.read().await.db;

    let tournament = if let Some(tournament) = db
        .collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .find_one(doc! { "_id": &group.tournament })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch tournament: {e}");

            Error::InternalError
        })? {
        tournament.id.unwrap()
    } else {
        return Err(Error::NotFound(String::from("Torneio")));
    };

    let group_id = db
        .collection(GROUPS_COLLECTION)
        .insert_one(Group::try_from(group)?)
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create team: {e}");

            Error::InternalError
        })?
        .inserted_id;

    db.collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .update_one(
            doc! { "_id": &tournament },
            doc! { "$push": { "groups": group_id } },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add group to tournament: {e}");

            Error::InternalError
        })?;

    event!(Level::INFO, "Successfully created group");

    Ok(())
}

#[utoipa::path(get, path = "/groups", tag = "Groups", responses((status = 200, description = "List of registered groups", body = Vec<GroupDto>)))]
#[instrument(skip(state))]
pub(crate) async fn get_groups(
    Extension(state): Extension<SharedState>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Listing all groups");

    let groups = state
        .read()
        .await
        .db
        .collection(GROUPS_COLLECTION)
        .find(Document::new())
        .await
        .unwrap()
        .try_collect::<Vec<Group>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't get all groups: {e}");

            Error::InternalError
        })?
        .into_iter()
        .map(GroupDto::from)
        .collect::<Vec<_>>();

    Ok(Json(groups))
}
