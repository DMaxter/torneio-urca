#![feature(iterator_try_collect)]

pub(crate) mod card;
mod config;
pub(crate) mod db;
pub(crate) mod entity;
pub(crate) mod error;
pub(crate) mod game;
pub(crate) mod goal;
pub(crate) mod group;
pub(crate) mod team;
pub(crate) mod tournament;
pub(crate) mod user;

use std::sync::Arc;

use axum::{Router, routing::post, serve};
pub use config::Config;
use tokio::{net::TcpListener, sync::RwLock};
use tower_http::add_extension::AddExtensionLayer;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

use crate::{
    card::route::assign_card,
    game::{route::add_game, route::get_games},
    goal::route::assign_goal,
    group::{add_group, get_groups},
    team::route::{add_team, get_teams},
    tournament::route::{add_tournament, get_tournaments},
    user::route::{add_user, get_users},
};

pub type SharedState = Arc<RwLock<Config>>;

pub async fn start_server(config: SharedState) {
    let app = Router::new()
        .route("/games", post(add_game).get(get_games))
        .route("/cards", post(assign_card))
        .route("/goals", post(assign_goal))
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
        card::route::assign_card,
        game::route::add_game,
        game::route::get_games,
        goal::route::assign_goal,
        group::add_group,
        group::get_groups,
        team::route::add_team,
        team::route::get_teams,
        tournament::route::add_tournament,
        tournament::route::get_tournaments,
        user::route::add_user,
        user::route::get_users
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
        tournament::CreateTournamentDto,
        tournament::TournamentDto,
        user::CreateUserDto,
        user::UserDto
    ))
)]
struct ApiDoc;
