from supabase import create_client, Client
from app.core.config import get_settings
from functools import lru_cache


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.
    
    Returns:
        Client: Initialized Supabase client
    """
    settings = get_settings()
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    ) 