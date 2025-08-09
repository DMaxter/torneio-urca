use std::env;

use dotenvy::dotenv;
use mongodb::{Client, Database, options::ClientOptions};
use tracing::{Level, event};

use crate::db::initialize;

const DEFAULT_HTTP_HOST: &str = "0.0.0.0";
const DEFAULT_HTTP_PORT: &str = "8000";

#[derive(Clone)]
pub struct Config {
    pub db: Database,
    pub listener: String,
}

impl Config {
    pub async fn new() -> Config {
        dotenv().expect("Couldn't find environment variable configuration");

        event!(Level::DEBUG, "Creating connection to database");
        let options = ClientOptions::parse(get_env_value(
            "DB_CONNECTION_STRING",
            Some("Database connection string not defined! Set DB_CONNECTION_STING variable"),
            None,
        ))
        .await
        .expect("Couldn't parse connection string");

        let client = Client::with_options(options).expect("Couldn't create database client");

        let db = client
            .default_database()
            .expect("Default database not defined");

        initialize(&db).await;

        event!(Level::DEBUG, "Parsing HTTP parameters");
        let listener = format!(
            "{0}:{1}",
            get_env_value("HTTP_HOST", None, Some(String::from(DEFAULT_HTTP_HOST))),
            get_env_value("HTTP_PORT", None, Some(String::from(DEFAULT_HTTP_PORT)))
        );

        Config { db, listener }
    }
}

fn get_env_value(var: &str, error: Option<&str>, default: Option<String>) -> String {
    if default.is_some() && error.is_some() {
        panic!("Provide either error or default, not both")
    }

    match env::var(var) {
        Ok(value) => value,
        Err(_) => {
            if let Some(default) = default {
                event!(
                    Level::WARN,
                    "Value for {var} not provided. Defaulting to {default}"
                );

                default
            } else {
                event!(Level::ERROR, error);
                panic!("Cannot continue program execution")
            }
        }
    }
}
