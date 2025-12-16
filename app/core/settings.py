from pydantic import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DATABASE_URL: str  # <-- this is the correct variable name

    class Config:
        env_file = ".env"


settings = Settings()
