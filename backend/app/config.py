# Configuration settings
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "London Bleeds"
    DATABASE_URL: str = "sqlite:///game.db"
    OPENAI_API_KEY: str = ""
    
    class Config:
        # Use absolute path to project root .env file
        # This ensures it works regardless of current working directory
        env_file = Path(__file__).parent.parent.parent / ".env"

settings = Settings()
