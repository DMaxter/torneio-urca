use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::entity::{Role, User};

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct CreateUserDto {
    pub name: String,
    pub birth_date: DateTime<Utc>,
    pub address: Option<String>,
    pub place_of_birth: Option<String>,
    pub fiscal_number: String,
}

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct UserDto {
    pub id: String,
    pub name: String,
    pub birth_date: DateTime<Utc>,
    pub address: Option<String>,
    pub place_of_birth: Option<String>,
    pub fiscal_number: String,
    pub confirmed: bool,
    pub roles: Vec<Role>,
}

impl From<User> for UserDto {
    fn from(value: User) -> Self {
        UserDto {
            id: value.id.unwrap().to_hex(),
            name: value.name,
            birth_date: value.birth_date,
            address: value.address,
            place_of_birth: value.place_of_birth,
            fiscal_number: value.fiscal_number,
            confirmed: value.confirmed,
            roles: value.roles,
        }
    }
}
