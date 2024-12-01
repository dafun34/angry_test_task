import os

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    bot_token: str
    bot_name: str
    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    base_dir: str = os.path.dirname(os.path.dirname(current_dir))

    django_host: str
    django_port: int

    db_host: str = Field(default="localhost")
    db_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str


config = Settings()
