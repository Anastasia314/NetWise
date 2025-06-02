"""
Configuration module for loading environment variables
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

@dataclass
class Config:
    """Configuration class to hold all settings"""
    telegram_token: str
    supabase_url: str
    supabase_key: str
    log_level: str

def load_config() -> Config:
    """Load and return configuration object"""
    return Config(
        telegram_token=TELEGRAM_BOT_TOKEN,
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY,
        log_level=LOG_LEVEL
    )

def get_bot_token() -> str:
    """Get the bot token from environment variables."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
    return token

def get_bot_username() -> str:
    """Get the bot username from environment variables."""
    username = os.getenv("TELEGRAM_BOT_USERNAME")
    if not username:
        raise ValueError("TELEGRAM_BOT_USERNAME environment variable is not set")
    return username

def get_supabase_url() -> str:
    """Get the Supabase URL from environment variables."""
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise ValueError("SUPABASE_URL environment variable is not set")
    return url

def get_supabase_key() -> str:
    """Get the Supabase key from environment variables."""
    key = os.getenv("SUPABASE_KEY")
    if not key:
        raise ValueError("SUPABASE_KEY environment variable is not set")
    return key 