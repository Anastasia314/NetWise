from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings
import urllib.parse

_settings = get_settings()

# Parse database URL to handle special characters
db_url = _settings.DATABASE_URL
parsed = urllib.parse.urlparse(db_url)
# Ensure the password is properly URL encoded
password = urllib.parse.quote_plus(parsed.password)
# Reconstruct the URL with encoded password
db_url = db_url.replace(parsed.password, password)

# Create SQLAlchemy engine with connection pool settings
engine = create_engine(
    db_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

def get_db_session() -> Session:
    """
    Get a new SQLAlchemy session.
    Returns:
        Session: SQLAlchemy session instance
    """
    return SessionLocal() 