from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://flypark:flypark@db:5432/flypark"
    secret_key: str = "dev-secret-key"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
