#![feature(iterator_try_collect)]

mod config;
pub(crate) mod db;
pub(crate) mod entity;
pub(crate) mod error;
pub(crate) mod team;
pub(crate) mod user;

use std::sync::Arc;

use axum::{Router, routing::post, serve};
pub use config::Config;
use tokio::{net::TcpListener, sync::RwLock};
use tower_http::add_extension::AddExtensionLayer;
use user::add_user;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

use crate::{
    team::{add_team, get_teams},
    user::get_users,
};

pub type SharedState = Arc<RwLock<Config>>;

pub async fn start_server(config: SharedState) {
    let app = Router::new()
        .route("/teams", post(add_team).get(get_teams))
        .route("/users", post(add_user).get(get_users))
        .merge(SwaggerUi::new("/swagger-ui").url("/api-docs/openapi.json", ApiDoc::openapi()))
        .layer(AddExtensionLayer::new(Arc::clone(&config)));

    serve(
        TcpListener::bind(&config.read().await.listener)
            .await
            .unwrap(),
        app,
    )
    .await
    .unwrap()
}

#[derive(OpenApi)]
#[openapi(
    paths(team::add_team, team::get_teams, user::add_user, user::get_users),
    components(schemas(team::CreateTeamDto, team::TeamDto, user::CreateUserDto, user::UserDto))
)]
struct ApiDoc;
