use mongodb::{Database, IndexModel, bson::doc};

use crate::entity::{Card, Game, GameRecord, Goal, User};

pub(crate) const CARDS_COLLECTION: &str = "cards";
pub(crate) const GAME_RECORDS_COLLECTION: &str = "game_records";
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
    db.create_collection(GAME_RECORDS_COLLECTION)
        .await
        .expect("Couldn't create game records collection");
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
                .keys(doc! { "group": 1, "scheduled_date": -1 })
                .build(),
        )
        .await
        .expect("Couldn't create index on games collection");
    db.collection::<GameRecord>(GAME_RECORDS_COLLECTION)
        .create_index(
            IndexModel::builder()
                .keys(doc! {"game": 1, "home_team": 1, "away_team": 1})
                .build(),
        )
        .await
        .expect("Couldn't create index on game records collection");
    db.collection::<Goal>(GOALS_COLLECTION)
        .create_index(IndexModel::builder().keys(doc! {"player": 1}).build())
        .await
        .expect("Couldn't create index on goals collection");
    db.collection::<User>(USERS_COLLECTION)
        .create_index(IndexModel::builder().keys(doc! { "team": 1 }).build())
        .await
        .expect("Couldn't create index on users collection");
}
