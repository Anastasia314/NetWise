"""
User service module.

This module contains service functions for user management,
including user profile retrieval, creation, and updates.
"""

from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from supabase import Client

from app.models.user_models import UserResponse, UserProfileUpdate
from app.db.user_repo import get_user_by_telegram_id, create_user, update_user_profile

# Constants for validation
MAX_SKILLS = 10
MAX_GOALS = 5
MAX_INTERESTS = 5

def get_user_profile_service(db_client: Client, telegram_id: int) -> Optional[UserResponse]:
    """
    Get a user's profile by their Telegram ID.
    
    Args:
        db_client: Supabase client instance
        telegram_id: Telegram ID of the user
        
    Returns:
        UserResponse if user exists, None otherwise
    """
    user = get_user_by_telegram_id(db_client, telegram_id)
    if not user:
        return None
    return UserResponse(**user)

def create_or_get_user_service(
    db_client: Client,
    telegram_id: int,
    name: Optional[str] = None,
    username: Optional[str] = None
) -> UserResponse:
    """
    Create a new user or get existing user by Telegram ID.
    
    Args:
        db_client: Supabase client instance
        telegram_id: Telegram ID of the user
        name: Optional name of the user
        username: Optional username (will be used as name if name not provided)
        
    Returns:
        UserResponse: User data
    """
    # Try to get existing user
    user = get_user_by_telegram_id(db_client, telegram_id)
    if user:
        return UserResponse(**user)
    
    # Create new user
    display_name = name or username or f"User{telegram_id}"
    user_data = create_user(
        db_client=db_client,
        telegram_id=telegram_id,
        name=display_name,
        username=username
    )
    return UserResponse(**user_data)

def update_user_profile_service(
    db_client: Client,
    telegram_id: int,
    profile_data_in: UserProfileUpdate
) -> UserResponse:
    """
    Update a user's profile.
    
    Args:
        db_client: Supabase client instance
        telegram_id: Telegram ID of the user
        profile_data_in: UserProfileUpdate model containing fields to update
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException: If user not found or validation fails
    """
    # Check if user exists
    user = get_user_by_telegram_id(db_client, telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    
    # Validate input data
    if profile_data_in.skills and len(profile_data_in.skills) > MAX_SKILLS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_SKILLS} skills allowed"
        )
    
    if profile_data_in.goals and len(profile_data_in.goals) > MAX_GOALS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_GOALS} goals allowed"
        )
    
    if profile_data_in.interests and len(profile_data_in.interests) > MAX_INTERESTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_INTERESTS} interests allowed"
        )
    
    # Update user profile
    updated_user = update_user_profile(
        db_client=db_client,
        telegram_id=telegram_id,
        profile_data=profile_data_in.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    
    return UserResponse(**updated_user)