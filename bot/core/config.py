from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # This will ignore extra fields in .env

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class Config:
    """Configuration settings for the bot."""
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    @classmethod
    def validate(cls) -> None:
        """Validate the configuration settings."""
        if not cls.API_BASE_URL:
            raise ValueError("API_BASE_URL environment variable is not set") 