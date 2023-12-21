from pydantic_settings import BaseSettings, SettingsConfigDict

from functools import lru_cache


class Settings(BaseSettings):
    APP_JWT_SECRET_KEY: str
    APP_JWT_EXPIRE_MINUTES: int
    APP_JWT_URL: str
    PASSWORD_ALGORITHM: str
    SQLALCHEMY_DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
