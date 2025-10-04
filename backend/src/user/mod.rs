mod dto;
pub(crate) mod route;

use bson::doc;
pub(crate) use dto::*;
use futures_util::TryStreamExt;
use mongodb::Database;
use tracing::{Level, event, instrument};

use crate::{
    db::{GAME_CALLS_COLLECTION, USERS_COLLECTION},
    entity::{Game, GameCall, Role, Team, User},
    error::Error,
};

#[instrument(skip(db))]
pub(crate) async fn get_user(db: &Database, user: &str) -> Result<User, Error> {
    event!(Level::DEBUG, "Getting user");

    match db
        .collection::<User>(USERS_COLLECTION)
        .find_one(doc! { "_id": user })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch user: {e}");

            Error::Internal
        }) {
        Ok(Some(user)) => {
            event!(Level::DEBUG, "Successfully got user");

            Ok(user)
        }
        Ok(None) => {
            event!(Level::ERROR, "Player doesn't exist");

            Err(Error::NotFound(String::from("Jogador")))
        }
        Err(e) => Err(e),
    }
}

#[instrument(skip(db))]
pub(crate) async fn get_player(db: &Database, player: &str) -> Result<User, Error> {
    let user = get_user(db, player).await?;

    if !user.roles.contains(&Role::Player) {
        Err(Error::UserNotPlayer)
    } else {
        Ok(user)
    }
}

#[instrument(skip(db))]
pub(crate) async fn check_player(
    db: &Database,
    team: &Team,
    game: &Game,
    player: &User,
) -> Result<(), Error> {
    event!(Level::DEBUG, "Validating player");

    let player_id = &player.id.unwrap();

    if !team.players.contains(player_id) {
        return Err(Error::PlayerNotInTeam);
    }

    let game_calls = db
        .collection::<GameCall>(GAME_CALLS_COLLECTION)
        .find(doc! { "$or": [{"_id": game.home_call}, {"_id": game.away_call}] })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch game calls: {e}");

            Error::Internal
        })?
        .try_collect::<Vec<_>>()
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't collect game calls: {e}");

            Error::Internal
        })?;

    if game_calls.len() != 2 {
        event!(Level::DEBUG, "Delivered: {}", game_calls.len());

        return Err(Error::GameCallsNotDelivered);
    }

    // Check if player is selected for the game
    if !game_calls[0].players.contains(player_id) && !game_calls[1].players.contains(player_id) {
        return Err(Error::PlayerNotInGame);
    }

    Ok(())
}
