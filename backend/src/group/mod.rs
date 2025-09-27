mod dto;

use axum::{Extension, Json, response::IntoResponse};
use bson::Document;
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use crate::{SharedState, db::GROUPS_COLLECTION, entity::Group, error::Error};
pub(crate) use dto::*;

#[utoipa::path(post, path = "/groups", tag = "Groups", request_body(content = CreateGroupDto), responses((status = 200, description = "Group registered")))]
#[instrument(skip(state))]
pub(crate) async fn add_group(
    Extension(state): Extension<SharedState>,
    Json(group): Json<CreateGroupDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating group");

    state
        .read()
        .await
        .db
        .collection(GROUPS_COLLECTION)
        .insert_one(Group::try_from(group)?)
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create team: {e}");

            Error::InternalError
        })?;

    event!(Level::INFO, "Successfully created team");

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
