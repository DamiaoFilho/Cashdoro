from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_username: str
    db_password: str
    db_name: str
    db_host: str = "localhost"
    db_port: int = 5432

    jwt_secret: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    @property
    def database_url(self) -> str:
        return URL.create(
            "postgresql+psycopg",
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
