"""
Main FastAPI application module.

This module creates and configures the FastAPI application instance,
including registering routers and middleware.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client

from app.api.users import router as user_router

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
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

# Register routers
app.include_router(user_router, prefix="/api/v1")

@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "status": "operational",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
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
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "version": settings.APP_VERSION,
                "environment": settings.APP_ENV
            }
        ) 