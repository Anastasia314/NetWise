"""
API dependencies for the NetWise application.

This module contains dependencies for API endpoints, such as retrieving the Supabase client
and extracting user identity from request headers.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase.client import Client
from typing import Annotated

from db.supabase_client import get_supabase_client
from services.user_service import UserService

security = HTTPBearer()

async def get_supabase_client() -> Client:
    """
    Get Supabase client instance.
    """
    return get_supabase_client()

async def get_current_telegram_id(x_telegram_id: str = Header(..., alias="X-Telegram-ID")) -> str:
    """
    Get current user's Telegram ID from X-Telegram-ID header.
    """
    if not x_telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Telegram-ID header is required"
        )
    return x_telegram_id

async def get_user_service(db_client: Client = Depends(get_supabase_client)) -> UserService:
    """
    Get UserService instance.
    """
    return UserService(db_client) 