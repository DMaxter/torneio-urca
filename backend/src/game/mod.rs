mod dto;
pub(crate) mod route;

use bson::{doc, oid::ObjectId, serialize_to_bson};
pub(crate) use dto::*;
use mongodb::Database;
use tracing::{Level, event, instrument};

use crate::{
    db::GAMES_COLLECTION,
    entity::{Game, GameEvent, GameStatus},
    error::Error,
};

#[instrument(skip(db))]
pub(crate) async fn get_game(db: &Database, game: &str) -> Result<Game, Error> {
    event!(Level::DEBUG, "Getting game");

    match db
        .collection::<Game>(GAMES_COLLECTION)
        .find_one(doc! { "_id": game })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch tournament: {e}");

            Error::Internal
        }) {
        Ok(Some(game)) => {
            event!(Level::DEBUG, "Successfully got game");

            Ok(game)
        }
        Ok(None) => {
            event!(Level::ERROR, "Couldn't find game");

            Err(Error::NotFound(String::from("Jogo")))
        }
        Err(e) => Err(e),
    }
}

#[instrument]
pub(crate) fn check_game_running(tournament: ObjectId, game: &Game) -> Result<(), Error> {
    event!(Level::DEBUG, "Validating game details");

    if game.tournament != tournament {
        return Err(Error::GameNotInTournament);
    } else if game.status != GameStatus::InProgress {
        return Err(Error::GameNotInProgress);
    }

    Ok(())
}

#[instrument(skip(db))]
pub(crate) async fn add_game_event(
    db: &Database,
    game: &ObjectId,
    event: &GameEvent,
) -> Result<(), Error> {
    db.collection::<Game>(GAMES_COLLECTION)
        .update_one(
            doc! { "_id": game },
            doc! { "$push": [{"events": serialize_to_bson(event).unwrap() }] },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't save game event: {e}");

            Error::Internal
        })?;

    Ok(())
}
