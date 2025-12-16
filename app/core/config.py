# app/core/config.py
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    FIREBASE_CREDENTIALS_FILE: str = "firebase_key.json"
    DATABASE_URL: str = "sqlite:///./autocompanion.db"
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
