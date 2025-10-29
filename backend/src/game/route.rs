use std::collections::HashMap;

use axum::{Extension, Json, response::IntoResponse};
use bson::{Document, doc};
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

use crate::{
    SharedState,
    db::{GAME_CALLS_COLLECTION, GAMES_COLLECTION, TOURNAMENTS_COLLECTION},
    entity::{Game, GameCall, Tournament},
    error::Error,
    game::{CreateGameDto, GameCallDto, GameDto},
    tournament::get_tournament,
};

#[utoipa::path(post, path = "/games", tag="Games", request_body(content = CreateGameDto), responses((status = 200, description = "Game created")))]
#[instrument(skip(state))]
pub(crate) async fn add_game(
    Extension(state): Extension<SharedState>,
    Json(game): Json<CreateGameDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Creating game");

    let db = &state.read().await.db;

    let tournament = get_tournament(&db, &game.tournament).await?.id.unwrap();

    let mut calls = db
        .collection(GAME_CALLS_COLLECTION)
        .insert_many(
            vec![game.home_call.to_owned(), game.away_call.to_owned()]
                .into_iter()
                .map(GameCall::try_from)
                .collect::<Result<Vec<_>, Error>>()?,
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create game calls: {e}");

            Error::Internal
        })?
        .inserted_ids;

    event!(Level::DEBUG, "Created game calls");

    let mut entity = Game::from(game.clone());

    entity.home_call = calls.remove(&0).unwrap().as_object_id();
    entity.away_call = calls.remove(&1).unwrap().as_object_id();

    let game_id = db
        .collection(GAMES_COLLECTION)
        .insert_one(entity.clone())
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't create game: {e}");

            Error::Internal
        })?
        .inserted_id
        .as_object_id()
        .unwrap();

    event!(Level::DEBUG, "Created game");

    db.collection::<GameCall>(GAME_CALLS_COLLECTION)
        .update_many(
            doc! {"$or": [{"_id": &entity.home_call}, {"_id": &entity.away_call}] },
            doc! {"$set": {"game": &game_id }},
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add game_id to game calls: {e}");

            Error::Internal
        })?;

    event!(Level::DEBUG, "Added game ID to game calls");

    db.collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .update_one(
            doc! { "_id": &tournament },
            doc! { "$push": { "games": &game_id } },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add game to tournament: {e}");

            Error::Internal
        })?;

    event!(Level::INFO, "Successfully created game");

    entity.id = Some(game_id);

    let mut dto = GameDto::from(entity.clone());

    dto.home_call = GameCallDto {
        id: entity.home_call.unwrap().to_hex(),
        team: game.home_call.team,
        game: game_id.to_hex(),
        ..Default::default()
    };
    dto.away_call = GameCallDto {
        id: entity.away_call.unwrap().to_hex(),
        team: game.away_call.team,
        game: game_id.to_hex(),
        ..Default::default()
    };

    Ok(Json(dto))
}

#[utoipa::path(get, path="/games", tag="Games", responses((status = 200, description = "List of games", body = Vec<GameDto>)))]
#[instrument(skip(state))]
pub(crate) async fn get_games(
    Extension(state): Extension<SharedState>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Listing all games");

    let db = &state.read().await.db;

    let games = db
        .collection(GAMES_COLLECTION)
        .find(Document::new())
        .await
        .unwrap()
        .try_collect::<Vec<Game>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't get all games: {e}");

            Error::Internal
        })?;

    let mut game_calls = db
        .collection(GAME_CALLS_COLLECTION)
        .find(Document::new())
        .await
        .unwrap()
        .try_collect::<Vec<GameCall>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't get all game calls: {e}");

            Error::Internal
        })?
        .into_iter()
        .map(|g| (g.id, GameCallDto::from(g)))
        .collect::<HashMap<_, _>>();

    Ok(Json(
        games
            .into_iter()
            .map(|g| {
                let home = game_calls.remove(&g.home_call).unwrap();
                let away = game_calls.remove(&g.away_call).unwrap();

                let mut dto = GameDto::from(g);

                dto.home_call = home;
                dto.away_call = away;

                dto
            })
            .collect::<Vec<_>>(),
    ))
}
