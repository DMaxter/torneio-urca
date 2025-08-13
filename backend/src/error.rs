use axum::{
    Json,
    http::StatusCode,
    response::{IntoResponse, Response},
};
use serde_json::json;
use std::{
    error::Error as StdError,
    fmt::{Display, Formatter, Result},
};

#[derive(Clone, Debug, PartialEq)]
pub(crate) enum Error {}

impl Error {
    fn to_code(&self) -> StatusCode {
        match self {
            _ => StatusCode::BAD_REQUEST,
        }
    }

    fn to_message(&self) -> String {
        match self {
            _ => String::from("Request not valid"),
        }
    }
}

impl StdError for Error {}

impl Display for Error {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        write!(f, "{}: {}", self.to_code(), self.to_message())
    }
}

impl IntoResponse for Error {
    fn into_response(self) -> Response {
        (
            self.to_code(),
            Json(json!({"error": self.to_code().to_string(), "message": self.to_message()})),
        )
            .into_response()
    }
}
