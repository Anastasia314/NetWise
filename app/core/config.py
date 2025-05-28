from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application settings
    APP_NAME: str = "NetWise"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API settings
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings() 