"""
Centralized application settings.
Loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./insightflow.db"

    # JWT Auth
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI
    GEMINI_API_KEY: str = ""
    AI_PROVIDER: str = "gemini"   # gemini
    # App
    UPLOAD_DIR: str = "uploads"
    ENV: str = "development"
    PROJECT_NAME: str = "InsightFlow AI"
    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
