use std::str::FromStr;

use bson::oid::ObjectId;
use serde::{Deserialize, Serialize};
use tracing::{Level, event};

use crate::{entity::Gender, error::Error, team::CreateTeamDto};

#[derive(Debug, Default, Deserialize, Serialize)]
pub struct Team {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub tournament: ObjectId,
    pub name: String,
    pub gender: Gender,
    pub responsible: ObjectId,
    pub main_coach: ObjectId,
    pub assistant_coach: Option<ObjectId>,
    pub players: Vec<ObjectId>, // Max: 14
    pub physiotherapist: ObjectId,
    pub first_deputy: ObjectId,
    pub second_deputy: Option<ObjectId>,
    pub valid: bool,
}

impl TryFrom<CreateTeamDto> for Team {
    type Error = Error;

    fn try_from(value: CreateTeamDto) -> Result<Self, Self::Error> {
        let assistant_id = match value.assistant_coach.map(|id| {
            ObjectId::from_str(&id).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert assistant coach ID: {e}");

                Error::InvalidId(String::from("treinador adjunto"))
            })
        }) {
            None => None,
            Some(Ok(v)) => Some(v),
            Some(Err(e)) => return Err(e),
        };

        let second_id = match value.second_deputy.map(|id| {
            ObjectId::from_str(&id).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert second deputy ID: {e}");

                Error::InvalidId(String::from("segundo delegado"))
            })
        }) {
            None => None,
            Some(Ok(v)) => Some(v),
            Some(Err(e)) => return Err(e),
        };

        Ok(Team {
            tournament: ObjectId::from_str(&value.tournament).unwrap(),
            name: value.name,
            gender: value.gender,
            responsible: ObjectId::from_str(&value.responsible).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert responsible ID: {e}");

                Error::InvalidId(String::from("responsável de equipa"))
            })?,
            main_coach: ObjectId::from_str(&value.main_coach).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert main coach ID: {e}");

                Error::InvalidId(String::from("treinador principal"))
            })?,
            assistant_coach: assistant_id,
            players: value
                .players
                .into_iter()
                .map(|id| {
                    ObjectId::from_str(&id).map_err(|e| {
                        event!(Level::ERROR, "Couldn't convert player ID: {e}");

                        Error::InvalidId(String::from("jogador"))
                    })
                })
                .try_collect::<Vec<ObjectId>>()?,
            physiotherapist: ObjectId::from_str(&value.physiotherapist).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert physiotherapist ID: {e}");

                Error::InvalidId(String::from("fisioterapeuta"))
            })?,
            first_deputy: ObjectId::from_str(&value.first_deputy).map_err(|e| {
                event!(Level::ERROR, "Couldn't convert first deputy ID: {e}");

                Error::InvalidId(String::from("primeiro delegado"))
            })?,
            second_deputy: second_id,
            ..Default::default()
        })
    }
}
