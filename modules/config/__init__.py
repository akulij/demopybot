from pydantic import (
    BaseSettings,
    PostgresDsn,
    Field,
)

class Settings(BaseSettings):
    database_uri: PostgresDsn = Field(env="DATABASE")
    qiwi_token: str = Field(env="QIWI_TOKEN")
    bot_token: str = Field(env="BOTTOKEN")

    class Config:
        env_file = ".env"


config = Settings()
