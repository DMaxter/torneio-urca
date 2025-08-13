use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::{entity::Role, user::CreateUserDto};

#[derive(Debug, Default, Deserialize, Serialize)]
pub(crate) struct User {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub name: String,
    #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime")]
    pub birth_date: DateTime<Utc>,
    pub address: Option<String>,
    pub place_of_birth: Option<String>,
    pub fiscal_number: String,
    pub confirmed: bool,
    pub roles: Vec<Role>,
    pub team_id: Option<ObjectId>,
}

impl From<CreateUserDto> for User {
    fn from(value: CreateUserDto) -> Self {
        User {
            name: value.name,
            birth_date: value.birth_date,
            address: value.place_of_birth,
            fiscal_number: value.fiscal_number,
            ..Default::default()
        }
    }
}
