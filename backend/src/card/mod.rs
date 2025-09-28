mod dto;

use axum::{Extension, Json, response::IntoResponse};
use bson::{doc, serialize_to_bson};
use futures_util::TryStreamExt;
use tracing::{Level, event, instrument};

pub(crate) use crate::card::dto::*;
use crate::{
    SharedState,
    db::{
        CARDS_COLLECTION, GAME_CALLS_COLLECTION, GAMES_COLLECTION, TEAMS_COLLECTION,
        TOURNAMENTS_COLLECTION, USERS_COLLECTION,
    },
    entity::{Card, Game, GameCall, GameEvent, GameStatus, Role, Team, Tournament, User},
    error::Error,
};

#[utoipa::path(post, path = "/cards", tag = "Cards", request_body = AssignCardDto, responses((status = 200, description = "Card assigned")))]
#[instrument(skip(state))]
pub(crate) async fn assign_card(
    Extension(state): Extension<SharedState>,
    Json(card): Json<AssignCardDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Assigning card to player");

    let db = &state.read().await.db;

    let tournament = if let Some(tournament) = db
        .collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .find_one(doc! { "_id": &card.tournament })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch tournament: {e}");

            Error::Internal
        })? {
        tournament.id.unwrap()
    } else {
        return Err(Error::NotFound(String::from("Torneio")));
    };

    let game = if let Some(game) = db
        .collection::<Game>(GAMES_COLLECTION)
        .find_one(doc! { "_id": &card.game })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch tournament: {e}");

            Error::Internal
        })? {
        game
    } else {
        return Err(Error::NotFound(String::from("Jogo")));
    };

    if game.tournament != tournament {
        return Err(Error::GameNotInTournament);
    } else if game.status != GameStatus::InProgress {
        return Err(Error::GameNotInProgress);
    }

    let team = if let Some(team) = db
        .collection::<Team>(TEAMS_COLLECTION)
        .find_one(doc! { "_id": &card.team })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch team: {e}");

            Error::Internal
        })? {
        team
    } else {
        event!(Level::ERROR, "Team doesn't exist");

        return Err(Error::NotFound(String::from("Equipa")));
    };

    let player = if let Some(user) = db
        .collection::<User>(USERS_COLLECTION)
        .find_one(doc! { "_id": &card.player })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch player: {e}");

            Error::Internal
        })? {
        user
    } else {
        event!(Level::ERROR, "Player doesn't exist");

        return Err(Error::NotFound(String::from("Jogador")));
    };

    event!(Level::DEBUG, "Player: {player:?}");

    let player_id = &player.id.unwrap();

    if !player.roles.contains(&Role::Player) {
        return Err(Error::UserNotPlayer);
    } else if !team.players.contains(&player_id) {
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

    let mut card = Card::from(card);

    card.team_name = team.name;
    card.player_name = player.name;
    card.period = game.current_period;

    db.collection::<Card>(CARDS_COLLECTION)
        .insert_one(&card)
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't assign card: {e}");

            Error::Internal
        })?;

    db.collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .update_one(
            doc! { "_id": &tournament },
            doc! { "&push": [{"cards": serialize_to_bson(&card).unwrap() }] },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add card to tournament: {e}");

            Error::Internal
        })?;

    let event = GameEvent::from(card);

    db.collection::<Game>(GAMES_COLLECTION)
        .update_one(
            doc! { "_id": &game.id },
            doc! { "$push": [{"events": serialize_to_bson(&event).unwrap() }] },
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't save game event: {e}");

            Error::Internal
        })?;

    // TODO: Broadcast event

    event!(Level::INFO, "Card assigned successfully");

    Ok(())
}
