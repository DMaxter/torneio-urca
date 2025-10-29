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
    tournament::get_tournament,
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

    let tournament = get_tournament(db, &group.tournament).await?.id;

    let mut entity = Group::try_from(group)?;

    let group_id = db
        .collection(GROUPS_COLLECTION)
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
            doc! { "$push": { "groups": group_id } },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add group to tournament: {e}");

            Error::Internal
        })?;

    event!(Level::INFO, "Successfully created group");

    entity.id = Some(group_id);

    Ok(Json(GroupDto::from(entity)))
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

            Error::Internal
        })?
        .into_iter()
        .map(GroupDto::from)
        .collect::<Vec<_>>();

    Ok(Json(groups))
}
