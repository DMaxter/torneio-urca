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

use crate::user::get_users;

pub type SharedState = Arc<RwLock<Config>>;

pub async fn start_server(config: SharedState) {
    let app = Router::new()
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
    paths(user::add_user, user::get_users),
    components(schemas(user::CreateUserDto, user::UserDto))
)]
struct ApiDoc;
