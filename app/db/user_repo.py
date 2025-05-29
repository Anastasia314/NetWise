"""
User repository module for handling all database operations related to users.
This module provides functions for creating, retrieving, and updating user records in Supabase.
"""

from typing import Optional
from datetime import datetime
from supabase import Client

from app.models.user_models import UserCreate, UserProfileUpdate, UserResponse

# These imports will be added in the next task
# from app.models.user_models import UserCreate, UserProfileUpdate, UserResponse 

def get_user_by_telegram_id(db_client: Client, telegram_id: int) -> Optional[UserResponse]:
    """
    Fetch a user by their Telegram ID from the Supabase users table.
    
    Args:
        db_client: Supabase client instance
        telegram_id: The Telegram ID of the user to fetch
        
    Returns:
        UserResponse if user is found, None otherwise
    """
    try:
        response = db_client.table("users").select("*").eq("telegram_id", telegram_id).execute()
        
        if not response.data:
            return None
            
        return UserResponse(**response.data[0])
    except Exception as e:
        # Log the error here if needed
        raise e 

def create_user(db_client: Client, user_in: UserCreate) -> UserResponse:
    """
    Create a new user in the Supabase users table.
    
    Args:
        db_client: Supabase client instance
        user_in: UserCreate model containing the user data to insert
        
    Returns:
        UserResponse containing the created user data
        
    Raises:
        Exception: If there's an error during database insertion
    """
    try:
        # Convert Pydantic model to dict and add timestamps
        user_data = user_in.model_dump()
        user_data.update({
            "created_at": datetime.now().isoformat(),
            "social_points": 0,
            "free_requests_remaining": 5,
            "is_active_in_search": True
        })
        
        # Insert the user data
        response = db_client.table("users").insert(user_data).execute()
        
        if not response.data:
            raise Exception("Failed to create user: No data returned from database")
            
        return UserResponse(**response.data[0])
    except Exception as e:
        # Log the error here if needed
        raise e

def update_user_profile(db_client: Client, telegram_id: int, profile_data: UserProfileUpdate) -> Optional[UserResponse]:
    """
    Update an existing user's profile in the Supabase users table.
    
    Args:
        db_client: Supabase client instance
        telegram_id: The Telegram ID of the user to update
        profile_data: UserProfileUpdate model containing the fields to update
        
    Returns:
        UserResponse containing the updated user data if successful, None if user not found
        
    Raises:
        Exception: If there's an error during database update
    """
    try:
        # Convert Pydantic model to dict, excluding unset fields
        update_data = profile_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Update the user data
        response = db_client.table("users").update(update_data).eq("telegram_id", telegram_id).execute()
        
        if not response.data:
            return None
            
        return UserResponse(**response.data[0])
    except Exception as e:
        # Log the error here if needed
        raise e 