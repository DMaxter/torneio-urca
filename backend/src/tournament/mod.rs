mod dto;
pub(crate) mod route;

use bson::doc;
use mongodb::Database;
use tracing::{Level, event, instrument};

use crate::{db::TOURNAMENTS_COLLECTION, entity::Tournament, error::Error};
pub(crate) use dto::*;

#[instrument(skip(db))]
pub(crate) async fn get_tournament(db: &Database, tournament: &str) -> Result<Tournament, Error> {
    match db
        .collection::<Tournament>(TOURNAMENTS_COLLECTION)
        .find_one(doc! { "_id": tournament })
        .await
        .map_err(|e| {
            event!(Level::ERROR, "Couldn't fetch tournament: {e}");

            Error::Internal
        }) {
        Ok(Some(tournament)) => Ok(tournament),
        Ok(None) => {
            event!(Level::ERROR, "Tournament not found");

            Err(Error::NotFound(String::from("Torneio")))
        }
        Err(e) => Err(e),
    }
}
