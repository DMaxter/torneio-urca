#![feature(iterator_try_collect)]

pub(crate) mod card;
mod config;
pub(crate) mod db;
pub(crate) mod entity;
pub(crate) mod error;
pub(crate) mod game;
pub(crate) mod group;
pub(crate) mod team;
pub(crate) mod tournament;
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
    card::assign_card,
    game::{add_game, get_games},
    group::{add_group, get_groups},
    team::{add_team, get_teams},
    tournament::{add_tournament, get_tournaments},
    user::get_users,
};

pub type SharedState = Arc<RwLock<Config>>;

pub async fn start_server(config: SharedState) {
    let app = Router::new()
        .route("/games", post(add_game).get(get_games))
        .route("/cards", post(assign_card))
        .route("/groups", post(add_group).get(get_groups))
        .route("/teams", post(add_team).get(get_teams))
        .route("/tournaments", post(add_tournament).get(get_tournaments))
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
    paths(
        card::assign_card,
        game::add_game,
        game::get_games,
        group::add_group,
        group::get_groups,
        team::add_team,
        team::get_teams,
        tournament::add_tournament,
        tournament::get_tournaments,
        user::add_user,
        user::get_users
    ),
    components(schemas(
        card::AssignCardDto,
        game::CreateGameDto,
        game::CreateGameCallDto,
        game::GameDto,
        game::GameCallDto,
        game::GameEventDto,
        group::CreateGroupDto,
        group::GroupDto,
        team::CreateTeamDto,
        team::TeamDto,
        tournament::TournamentDto,
        user::CreateUserDto,
        user::UserDto
    ))
)]
struct ApiDoc;
