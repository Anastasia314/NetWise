"""
User service module for handling business logic related to user management.
This module provides service functions that interact with the user repository
and implement business rules for user operations.
"""

from typing import Optional
from fastapi import HTTPException
from supabase import Client

from app.models.user_models import UserCreate, UserProfileUpdate, UserResponse
from app.db.user_repo import get_user_by_telegram_id, create_user, update_user_profile

# Constants for validation
MAX_SKILLS = 10
MAX_GOALS = 5
MAX_INTERESTS = 5

def get_user_profile_service(db_client: Client, telegram_id: int) -> Optional[UserResponse]:
    """
    Service function to get a user's profile by their Telegram ID.
    
    Args:
        db_client: Supabase client instance
        telegram_id: The Telegram ID of the user to fetch
        
    Returns:
        UserResponse if user is found, None otherwise
        
    Note:
        This service function currently just passes through to the repository layer.
        Additional business logic can be added here as needed.
    """
    return get_user_by_telegram_id(db_client, telegram_id)

def create_or_get_user_service(
    db_client: Client,
    telegram_id: int,
    name: Optional[str] = None,
    username: Optional[str] = None
) -> UserResponse:
    """
    Service function to create a new user or get an existing one by Telegram ID.
    
    Args:
        db_client: Supabase client instance
        telegram_id: The Telegram ID of the user
        name: Optional name of the user
        username: Optional username (currently not used, as we use name field)
        
    Returns:
        UserResponse containing the user data
        
    Note:
        If a user with the given telegram_id exists, returns that user.
        Otherwise, creates a new user with the provided information.
        The username parameter is included for future use but currently maps to name.
    """
    # Try to get existing user
    existing_user = get_user_by_telegram_id(db_client, telegram_id)
    if existing_user:
        return existing_user
        
    # Create new user if not found
    user_create = UserCreate(
        telegram_id=telegram_id,
        name=name or username  # Use name if provided, fallback to username
    )
    return create_user(db_client, user_create)

def update_user_profile_service(
    db_client: Client,
    telegram_id: int,
    profile_data_in: UserProfileUpdate
) -> UserResponse:
    """
    Service function to update a user's profile.
    
    Args:
        db_client: Supabase client instance
        telegram_id: The Telegram ID of the user to update
        profile_data_in: UserProfileUpdate model containing the fields to update
        
    Returns:
        UserResponse containing the updated user data
        
    Raises:
        HTTPException: If the user is not found (404) or if validation fails (400)
    """
    # Validate list lengths if provided
    if profile_data_in.skills is not None and len(profile_data_in.skills) > MAX_SKILLS:
        raise HTTPException(
            status_code=400,
            detail=f"Too many skills provided. Maximum allowed is {MAX_SKILLS}"
        )
    
    if profile_data_in.goals is not None and len(profile_data_in.goals) > MAX_GOALS:
        raise HTTPException(
            status_code=400,
            detail=f"Too many goals provided. Maximum allowed is {MAX_GOALS}"
        )
    
    if profile_data_in.interests is not None and len(profile_data_in.interests) > MAX_INTERESTS:
        raise HTTPException(
            status_code=400,
            detail=f"Too many interests provided. Maximum allowed is {MAX_INTERESTS}"
        )
    
    # Attempt to update the user
    updated_user = update_user_profile(db_client, telegram_id, profile_data_in)
    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    return updated_user