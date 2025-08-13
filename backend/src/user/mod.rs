mod dto;

use bson::Document;
pub(crate) use dto::*;
use futures_util::TryStreamExt;
use mongodb::error::Error as MongoError;

use axum::{Extension, Json, response::IntoResponse};

use crate::{
    SharedState,
    db::{self, USERS_COLLECTION},
    entity::User,
    error::Error,
};

#[utoipa::path(post, path = "/users", tag="Users", request_body(content = UserDto), responses((status = 200, description = "User registered")))]
pub(crate) async fn add_user(
    Extension(state): Extension<SharedState>,
    Json(user): Json<CreateUserDto>,
) -> Result<impl IntoResponse, Error> {
    state
        .read()
        .await
        .db
        .collection(USERS_COLLECTION)
        .insert_one(User::from(user))
        .await;

    Ok(())
}

#[utoipa::path(get, path="/users", tag="Users", responses((status = 200, description = "List of users", body = Vec<UserDto>)))]
pub(crate) async fn get_users(
    Extension(state): Extension<SharedState>,
) -> Result<impl IntoResponse, Error> {
    Ok(Json(
        state
            .read()
            .await
            .db
            .collection(USERS_COLLECTION)
            .find(Document::new())
            .await
            .unwrap()
            .try_collect::<Vec<User>>()
            .await
            .unwrap()
            .into_iter()
            .map(|user| UserDto::from(user))
            .collect::<Vec<_>>(),
    ))
}
