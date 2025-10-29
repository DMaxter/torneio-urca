use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_with::serde_as;

use crate::{
    entity::{Gender, Role},
    user::CreateUserDto,
};

#[serde_as]
#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub(crate) struct User {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub name: String,
    pub gender: Gender,
    #[serde_as(as = "bson::serde_helpers::datetime::FromChrono04DateTime")]
    pub birth_date: DateTime<Utc>,
    pub address: Option<String>,
    pub place_of_birth: Option<String>,
    pub fiscal_number: String,
    pub confirmed: bool,
    pub roles: Vec<Role>,
}

impl From<CreateUserDto> for User {
    fn from(value: CreateUserDto) -> Self {
        User {
            name: value.name,
            gender: value.gender,
            birth_date: value.birth_date,
            address: value.place_of_birth,
            fiscal_number: value.fiscal_number,
            roles: value.roles,
            ..Default::default()
        }
    }
}
