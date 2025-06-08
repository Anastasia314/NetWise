from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "NetWise Bot")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    model_config = {
        "extra": "allow"
    }

    def validate_settings(self) -> None:
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_settings()
    return settings