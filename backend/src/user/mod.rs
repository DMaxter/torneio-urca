mod dto;

use bson::Document;
pub(crate) use dto::*;
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use axum::{Extension, Json, response::IntoResponse};

use crate::{SharedState, db::USERS_COLLECTION, entity::User, error::Error};

#[utoipa::path(post, path = "/users", tag="Users", request_body(content = UserDto), responses((status = 200, description = "User registered")))]
#[instrument(skip(state))]
pub(crate) async fn add_user(
    Extension(state): Extension<SharedState>,
    Json(user): Json<CreateUserDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating user");

    state
        .read()
        .await
        .db
        .collection(USERS_COLLECTION)
        .insert_one(User::from(user))
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create user: {e}");

            Error::Internal
        })?;

    event!(Level::INFO, "Successfully created user");

    Ok(())
}

#[utoipa::path(get, path="/users", tag="Users", responses((status = 200, description = "List of users", body = Vec<UserDto>)))]
#[instrument(skip(state))]
pub(crate) async fn get_users(
    Extension(state): Extension<SharedState>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Listing all users");

    let users = state
        .read()
        .await
        .db
        .collection(USERS_COLLECTION)
        .find(Document::new())
        .await
        .unwrap()
        .try_collect::<Vec<User>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't get all users: {e}");

            Error::Internal
        })?
        .into_iter()
        .map(UserDto::from)
        .collect::<Vec<_>>();

    Ok(Json(users))
}
