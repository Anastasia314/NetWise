from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Bot settings
    BOT_TOKEN: str
    
    # Database settings
    DATABASE_URL: str
    
    # API settings
    API_URL: str
    API_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 