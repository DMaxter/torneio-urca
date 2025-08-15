use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Default, Deserialize, Serialize, ToSchema)]
#[serde(rename_all = "lowercase")]
pub enum Gender {
    #[default]
    Male,
    Female,
}
