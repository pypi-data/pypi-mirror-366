from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DB_URI = "postgresql+asyncpg://user:password@localhost:5432/database"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    database_uri: str = Field(default=DEFAULT_DB_URI)
    secret_key: str = Field(default="Secret_Key")


settings = Settings()
