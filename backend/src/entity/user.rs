use bson::oid::ObjectId;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::entity::Role;

#[derive(Debug, Deserialize, Serialize)]
pub(crate) struct User {
    #[serde(rename = "_id", skip_serializing_if = "Option::is_none")]
    pub id: Option<ObjectId>,
    pub name: Option<String>,
    #[serde(with = "bson::serde_helpers::chrono_datetime_as_bson_datetime_optional")]
    pub birth_date: Option<DateTime<Utc>>,
    pub address: Option<String>,
    pub place_of_birth: Option<String>,
    pub fiscal_number: String,
    pub confirmed: bool,
    pub roles: Vec<Role>,
    pub team_id: Option<ObjectId>,
}
