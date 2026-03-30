from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    db_connection_string: str
    http_host: str = "0.0.0.0"
    http_port: int = 8000
    database_name: str = "pm_tournament"
    jwt_secret: str
    production: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
