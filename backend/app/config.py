from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LifeOS API"
    environment: str = "development"
    debug: bool = False

    # mysql+pymysql://usuario:contraseña@host:puerto/base
    database_url: str = "mysql+pymysql://lifeos:lifeos@localhost:3306/lifeos?charset=utf8mb4"


@lru_cache
def get_settings() -> Settings:
    return Settings()
