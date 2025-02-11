from functools import lru_cache

# from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_URL: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    USER_POOL_ID: str
    REGION: str
    SENDER_MAIL: str
    SERVICE_NAME: str
    ENVIRONMENT: str

    class Config:
        env_file = './.env'


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
