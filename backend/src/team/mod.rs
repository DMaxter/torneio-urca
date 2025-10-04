mod dto;
pub(crate) mod route;

use bson::doc;
pub(crate) use dto::*;
use mongodb::Database;
use tracing::{Level, event, instrument};

use crate::{db::TEAMS_COLLECTION, entity::Team, error::Error};

#[instrument(skip(db))]
pub(crate) async fn get_team(db: &Database, team: &str) -> Result<Team, Error> {
    event!(Level::DEBUG, "Getting team");

    match db
        .collection::<Team>(TEAMS_COLLECTION)
        .find_one(doc! { "_id": team })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch team: {e}");

            Error::Internal
        }) {
        Ok(Some(team)) => {
            event!(Level::DEBUG, "Successfully got team");

            Ok(team)
        }
        Ok(None) => {
            event!(Level::ERROR, "Team doesn't exist");

            return Err(Error::NotFound(String::from("Equipa")));
        }
        Err(e) => Err(e),
    }
}
