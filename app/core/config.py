from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    db_url: str = Field(
        default="postgresql+psycopg2://carms_app:carms_secret@postgres:5432/carms",
        env="DB_URL",
    )
    env: str = Field(default="local", env="ENV")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
