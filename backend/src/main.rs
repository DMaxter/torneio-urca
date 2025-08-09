use pm_tournament::Config;
use tracing::{Level, event};
use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() {
    // Set logging
    let subscriber = tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::builder()
                .with_default_directive(Level::INFO.into())
                .from_env_lossy(),
        )
        .finish();

    tracing::subscriber::set_global_default(subscriber).expect("Failed to set tracing subscriber");

    // Get configuration parameters
    event!(Level::INFO, "Loading configuration");
    let config = Config::new().await;
    event!(Level::INFO, "Configuration successfully loaded");

    // Start server

    event!(Level::INFO, "Listening on {0}", config.listener);
}
