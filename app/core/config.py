from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Application
    APP_TITLE: str = "Privacy Rights API"
    APP_DESCRIPTION: str = "GDPR/CCPA Data Subject Request Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/privacy_rights"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    API_KEY_PREFIX: str = "pra_live_"


settings = Settings()
