use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::entity::Group;

#[derive(Debug, Deserialize, ToSchema)]
pub(crate) struct CreateGroupDto {
    pub name: String,
    pub teams: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize, ToSchema)]
pub(crate) struct GroupDto {
    pub id: String,
    pub name: String,
    pub teams: Vec<String>,
}

impl From<Group> for GroupDto {
    fn from(value: Group) -> Self {
        GroupDto {
            id: value.id.unwrap().to_hex(),
            name: value.name,
            teams: value.teams.into_iter().map(|id| id.to_hex()).collect(),
        }
    }
}
