from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LifeOS API"
    environment: str = "development"
    debug: bool = False

    database_url: str = "mysql+pymysql://lifeos:lifeos@localhost:3306/lifeos?charset=utf8mb4"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    jwt_secret: SecretStr = Field(min_length=32)
    access_token_days: int = Field(default=30, ge=1, le=365)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @field_validator("database_url")
    @classmethod
    def use_pymysql_driver(cls, url: str) -> str:
        if url.startswith("mysql://"):
            url = "mysql+pymysql://" + url.removeprefix("mysql://")
        if url.startswith("mysql+pymysql://") and "charset=" not in url:
            url += ("&" if "?" in url else "?") + "charset=utf8mb4"
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings() 
