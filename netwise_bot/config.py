"""
Configuration module for loading environment variables
"""

import os
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

def get_supabase_url() -> str:
    """Get Supabase URL from environment variables."""
    return SUPABASE_URL

def get_supabase_key() -> str:
    """Get Supabase key from environment variables."""
    return SUPABASE_KEY 