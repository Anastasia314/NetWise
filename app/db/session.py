from supabase import create_client, Client
from app.config import get_settings

_settings = get_settings()

def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    Returns:
        Client: Supabase client instance
    """
    return create_client(
        supabase_url=_settings.SUPABASE_URL,
        supabase_key=_settings.SUPABASE_KEY
    ) 