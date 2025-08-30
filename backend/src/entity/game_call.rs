use std::str::FromStr;

use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};
use tracing::{Level, event};

use crate::{error::Error, game::CreateGameCallDto};

#[derive(Debug, Default, Deserialize, Serialize)]
pub(crate) struct GameCall {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub game: Option<ObjectId>,
    pub team: ObjectId,
    pub players: Vec<ObjectId>,
    pub deputy: Option<ObjectId>,
}

impl TryFrom<CreateGameCallDto> for GameCall {
    type Error = Error;

    fn try_from(value: CreateGameCallDto) -> Result<Self, Self::Error> {
        Ok(GameCall {
            team: ObjectId::from_str(&value.team).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert team ID: {e}");

                Error::InvalidId(String::from("equipa"))
            })?,
            ..Default::default()
        })
    }
}
