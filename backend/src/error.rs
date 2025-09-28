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
use tracing::{Level, event};

#[derive(Clone, Debug, PartialEq)]
pub(crate) enum Error {
    GameCallsNotDelivered,
    GameNotInProgress,
    GameNotInTournament,
    Internal,
    InvalidId(String),
    NotFound(String),
    PlayerNotInGame,
    PlayerNotInTeam,
    UserNotPlayer,
}

impl Error {
    fn to_code(&self) -> StatusCode {
        match self {
            Error::GameCallsNotDelivered | Error::GameNotInProgress | Error::UserNotPlayer => {
                StatusCode::FORBIDDEN
            }
            Error::GameNotInTournament | Error::PlayerNotInGame | Error::PlayerNotInTeam => {
                StatusCode::PRECONDITION_REQUIRED
            }
            Error::InvalidId(_) => StatusCode::BAD_REQUEST,
            Error::Internal => StatusCode::INTERNAL_SERVER_ERROR,
            Error::NotFound(_) => StatusCode::NOT_FOUND,
        }
    }

    fn to_message(&self) -> String {
        match self {
            Error::GameCallsNotDelivered => {
                String::from("As fichas de jogo ainda não foram entregues")
            }
            Error::GameNotInProgress => String::from("O jogo não está a decorrer"),
            Error::Internal => String::from("Erro interno"),
            Error::InvalidId(msg) => format!("ID inválido para {msg}"),
            Error::NotFound(msg) => format!("{msg} não existente"),
            Error::PlayerNotInGame => String::from("Jogador não alocado ao jogo"),
            Error::PlayerNotInTeam => String::from("Jogador não alocado à equipa"),
            Error::GameNotInTournament => String::from("Jogo não alocado ao torneio"),
            Error::UserNotPlayer => String::from("Utilizador não é um jogador"),
        }
    }

    fn log_error(&self) {
        match self {
            Error::GameCallsNotDelivered => {
                event!(Level::ERROR, "Game calls haven't been delivered");
            }
            Error::GameNotInProgress => event!(Level::ERROR, "Game is not in progress"),
            Error::GameNotInTournament => {
                event!(Level::ERROR, "Game doesn't belong to this tournament")
            }
            Error::Internal | Error::InvalidId(_) | Error::NotFound(_) => (),
            Error::PlayerNotInGame => event!(Level::ERROR, "Player doesn't belong to this game"),
            Error::PlayerNotInTeam => event!(Level::ERROR, "Player doesn't belong to this team"),
            Error::UserNotPlayer => event!(Level::ERROR, "User isn't a player"),
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
        self.log_error();

        (
            self.to_code(),
            Json(json!({"error": self.to_string(), "message": self.to_message()})),
        )
            .into_response()
    }
}
