from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://cyj@localhost:5432/test"
    secret_key: str = "eEfWSKOU99t2ZdfPJ2YILQR1D3BsCl-f50HOei1ZxzQ"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
