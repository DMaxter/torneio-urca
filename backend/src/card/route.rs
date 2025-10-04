use axum::{Extension, Json, response::IntoResponse};
use bson::{doc, serialize_to_bson};
use tracing::{Level, event, instrument};

use crate::{
    SharedState,
    card::AssignCardDto,
    db::{CARDS_COLLECTION, TOURNAMENTS_COLLECTION},
    entity::{Card, GameEvent, Tournament},
    error::Error,
    game::{add_game_event, check_game_running, get_game},
    team::get_team,
    tournament::get_tournament,
    user::{check_player, get_player},
};

#[utoipa::path(post, path = "/cards", tag = "Cards", request_body = AssignCardDto, responses((status = 200, description = "Card assigned")))]
#[instrument(skip(state))]
pub(crate) async fn assign_card(
    Extension(state): Extension<SharedState>,
    Json(card): Json<AssignCardDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Assigning card to player");

    let db = &state.read().await.db;

    let tournament = get_tournament(db, &card.tournament).await?.id.unwrap();

    let game = get_game(db, &card.game).await?;

    check_game_running(tournament, &game)?;

    let team = get_team(db, &card.team).await?;

    let player = get_player(db, &card.player).await?;

    event!(Level::DEBUG, "Player: {player:?}");

    check_player(db, &team, &game, &player).await?;

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

    add_game_event(db, &game.id.unwrap(), &event).await?;

    // TODO: Broadcast event

    event!(Level::INFO, "Card assigned successfully");

    Ok(())
}
