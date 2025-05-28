from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="NetWise - A Telegram bot for network monitoring and management",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "status": "operational",
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the application status.
    Checks:
    - Application is running
    - Database connection is available
    """
    try:
        # Test database connection
        supabase = get_supabase_client()
        # Simple query to test connection
        supabase.table("users").select("count", count="exact").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "version": settings.APP_VERSION
        }, 500 