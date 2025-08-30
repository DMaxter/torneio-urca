use mongodb::{Database, IndexModel, bson::doc};

use crate::entity::{Card, Game, GameCall, Goal, User};

pub(crate) const CARDS_COLLECTION: &str = "cards";
pub(crate) const GAME_CALLS_COLLECTION: &str = "game_calls";
pub(crate) const GAMES_COLLECTION: &str = "games";
pub(crate) const GOALS_COLLECTION: &str = "goals";
pub(crate) const TEAMS_COLLECTION: &str = "teams";
pub(crate) const USERS_COLLECTION: &str = "users";

pub(crate) async fn initialize(db: &Database) {
    // Create collections
    db.create_collection(CARDS_COLLECTION)
        .await
        .expect("Couldn't create cards collection");
    db.create_collection(GAMES_COLLECTION)
        .await
        .expect("Couldn't create games collection");
    db.create_collection(GAME_CALLS_COLLECTION)
        .await
        .expect("Couldn't create game calls collection");
    db.create_collection(GOALS_COLLECTION)
        .await
        .expect("Couldn't create goals collection");
    db.create_collection(TEAMS_COLLECTION)
        .await
        .expect("Couldn't create teams collection");
    db.create_collection(USERS_COLLECTION)
        .await
        .expect("Couldn't create users collection");

    // Create indexes
    db.collection::<Card>(CARDS_COLLECTION)
        .create_index(
            IndexModel::builder()
                .keys(doc! { "player_id": 1, "team_id": 1, "date": -1, "game": -1})
                .build(),
        )
        .await
        .expect("Couldn't create index on cards collection");
    db.collection::<Game>(GAMES_COLLECTION)
        .create_index(
            IndexModel::builder()
                .keys(doc! { "status": 1, "scheduled_date": -1 })
                .build(),
        )
        .await
        .expect("Couldn't create index on games collection");
    db.collection::<GameCall>(GAME_CALLS_COLLECTION)
        .create_index(
            IndexModel::builder()
                .keys(doc! {"game": 1, "team": 1})
                .build(),
        )
        .await
        .expect("Couldn't create index on game calls collection");
    db.collection::<Goal>(GOALS_COLLECTION)
        .create_index(IndexModel::builder().keys(doc! {"player": 1}).build())
        .await
        .expect("Couldn't create index on goals collection");
    db.collection::<User>(USERS_COLLECTION)
        .create_index(IndexModel::builder().keys(doc! { "team": 1 }).build())
        .await
        .expect("Couldn't create index on users collection");
}
