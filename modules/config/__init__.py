from pydantic import (
    BaseSettings,
    PostgresDsn,
    Field
)

class Settings(BaseSettings):
    database_uri: PostgresDsn = Field(env="DATABASE")

    class Config:
        env_file = ".env"


config = Settings()
