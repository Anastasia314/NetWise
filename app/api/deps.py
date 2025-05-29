"""
API dependencies for the NetWise application.

This module contains dependencies for API endpoints, such as retrieving the Supabase client
and extracting user identity from request headers.
"""

from fastapi import Depends, Header, HTTPException
from supabase import Client

from app.db.supabase_client import get_supabase_client as get_db_client
from app.services.user_service import (
    create_or_get_user_service,
    get_user_profile_service,
    update_user_profile_service
)

def get_supabase_client() -> Client:
    """
    Dependency to get Supabase client instance.
    
    Returns:
        Client: Initialized Supabase client
    """
    return get_db_client()

def get_current_telegram_id(x_telegram_id: int = Header(..., description="Telegram user ID")) -> int:
    """
    Dependency to extract and validate Telegram ID from request header.
    
    Args:
        x_telegram_id (int): Telegram user ID from X-Telegram-Id header
        
    Returns:
        int: Validated Telegram user ID
        
    Raises:
        HTTPException: If Telegram ID is not provided or invalid
    """
    if not x_telegram_id:
        raise HTTPException(
            status_code=400,
            detail="X-Telegram-Id header is required"
        )
    return x_telegram_id

def get_user_service():
    """
    Dependency to get user service functions.
    
    Returns:
        dict: Dictionary containing user service functions
    """
    return {
        "create_or_get_user": create_or_get_user_service,
        "get_user_profile": get_user_profile_service,
        "update_user_profile": update_user_profile_service
    } 