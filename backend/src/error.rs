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
pub(crate) enum Error {
    InternalError,
    InvalidId(String),
}

impl Error {
    fn to_code(&self) -> StatusCode {
        match self {
            Error::InvalidId(_) => StatusCode::BAD_REQUEST,
            _ => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }

    fn to_message(&self) -> String {
        match self {
            Error::InvalidId(msg) => format!("ID inválido para {msg}"),
            _ => String::from("Erro interno"),
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
