use std::str::FromStr;

use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};
use tracing::{Level, event};

use crate::{error::Error, group::CreateGroupDto};

#[derive(Debug, Default, Deserialize, Serialize)]
pub(crate) struct Group {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub tournament: ObjectId,
    pub name: String,
    pub teams: Vec<ObjectId>,
}

impl TryFrom<CreateGroupDto> for Group {
    type Error = Error;

    fn try_from(value: CreateGroupDto) -> Result<Self, Self::Error> {
        Ok(Group {
            tournament: ObjectId::from_str(&value.tournament).unwrap(),
            name: value.name,
            teams: value
                .teams
                .into_iter()
                .map(|id| {
                    ObjectId::from_str(&id).map_err(|e| {
                        event!(Level::ERROR, "Couldn't convert team ID: {e}");

                        Error::InvalidId(String::from("equipa"))
                    })
                })
                .try_collect::<Vec<ObjectId>>()?,
            ..Default::default()
        })
    }
}
