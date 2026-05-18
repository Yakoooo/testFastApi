from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "testFastApi"
    debug: bool = False

    database_url: str
    test_database_url: str | None = None
    secret_key: str
    algorithm: str = "HS236"
    access_token_expire_minutes: int = 60

    cors_origins: list[str] = []

settings = Settings()
