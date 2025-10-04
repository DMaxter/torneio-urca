use axum::{Extension, Json, response::IntoResponse};
use bson::{doc, serialize_to_bson};
use tracing::{Level, event, instrument};

use crate::{
    SharedState,
    db::{GOALS_COLLECTION, TOURNAMENTS_COLLECTION},
    entity::{GameEvent, Goal, Tournament},
    error::Error,
    game::{add_game_event, check_game_running, get_game},
    goal::AssignGoalDto,
    team::get_team,
    tournament::get_tournament,
    user::{check_player, get_player},
};

#[utoipa::path(post, path = "/goals", tag = "Goals", request_body = AssignGoalDto, responses((status = 200, description = "Goal assigned")))]
#[instrument(skip(state))]
pub(crate) async fn assign_goal(
    Extension(state): Extension<SharedState>,
    Json(goal): Json<AssignGoalDto>,
) -> Result<impl IntoResponse, Error> {
    event!(Level::INFO, "Assigning goal to player");

    let db = &state.read().await.db;

    let tournament = get_tournament(db, &goal.tournament).await?.id.unwrap();

    let game = get_game(db, &goal.game).await?;

    check_game_running(tournament, &game)?;

    let team = get_team(db, &goal.team).await?;

    let player = get_player(db, &goal.player).await?;

    event!(Level::DEBUG, "Player: {player:?}");

    let player_id = &player.id.unwrap();

    if !team.players.contains(player_id) {
        return Err(Error::PlayerNotInTeam);
    }

    check_player(db, &team, &game, &player).await?;

    let mut goal = Goal::from(goal);

    goal.team_name = team.name;
    goal.player_name = player.name;
    goal.period = game.current_period;

    db.collection::<Goal>(GOALS_COLLECTION)
        .insert_one(&goal)
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't assign goal: {e}");

            Error::Internal
        })?;

    db.collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .update_one(
            doc! {"_id": &tournament},
            doc! { "&push": [{"goals": serialize_to_bson(&goal).unwrap()}]},
        )
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't add goal to tournament: {e}");

            Error::Internal
        })?;

    let event = GameEvent::from(goal);

    add_game_event(db, &game.id.unwrap(), &event).await?;

    // TODO: Broadcast event

    event!(Level::INFO, "Goal assigned successfully");

    Ok(())
}
