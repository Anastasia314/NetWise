"""
User-related API endpoints.

This module contains all the API endpoints related to user management,
including user onboarding, profile retrieval, and profile updates.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from typing import Optional

from app.models.user_models import UserCreate, UserProfileUpdate, UserResponse
from app.api.deps import get_supabase_client, get_current_telegram_id, get_user_service
from supabase import Client

# Create router instance
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden - Not authorized to access this resource"},
        422: {"description": "Validation error"}
    },
)

@router.post(
    "/onboard",
    response_model=UserResponse,
    responses={
        201: {
            "description": "User successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "telegram_id": 123456789,
                        "name": "John Doe",
                        "role": "Software Engineer",
                        "industry": "Technology",
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                        "goals": ["Learn AI", "Network with professionals"],
                        "interests": ["Machine Learning", "Web Development"],
                        "social_points": 0,
                        "free_requests_remaining": 5,
                        "subscription_tier": "free",
                        "is_active_in_search": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        200: {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {
                        "telegram_id": 123456789,
                        "name": "John Doe",
                        "role": "Software Engineer",
                        "industry": "Technology",
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                        "goals": ["Learn AI", "Network with professionals"],
                        "interests": ["Machine Learning", "Web Development"],
                        "social_points": 100,
                        "free_requests_remaining": 3,
                        "subscription_tier": "premium",
                        "is_active_in_search": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-05-29T12:00:00Z"
                    }
                }
            }
        }
    }
)
async def onboard_user(
    name: Optional[str] = None,
    username: Optional[str] = None,
    telegram_id: int = Depends(get_current_telegram_id),
    db_client: Client = Depends(get_supabase_client),
    user_service: dict = Depends(get_user_service)
) -> UserResponse:
    """
    Onboard a new user or get existing user profile.
    
    This endpoint is used to create a new user profile or retrieve an existing one.
    The user's Telegram ID is required and must be provided in the X-Telegram-Id header.
    
    Args:
        name: Optional display name for the user
        username: Optional username (will be used as name if name not provided)
        telegram_id: User's Telegram ID (from X-Telegram-Id header)
        db_client: Supabase client instance
        user_service: User service functions
        
    Returns:
        UserResponse: User profile data
        
    Raises:
        HTTPException: If there's an error creating or retrieving the user
    """
    user = user_service["create_or_get_user"](
        db_client=db_client,
        telegram_id=telegram_id,
        name=name,
        username=username
    )
    
    # If user already exists, return 200 instead of 201
    if user.created_at == user.updated_at:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=user.model_dump()
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=user.model_dump()
    )

@router.get(
    "/{path_telegram_id}/profile",
    response_model=UserResponse,
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "telegram_id": 123456789,
                        "name": "John Doe",
                        "role": "Software Engineer",
                        "industry": "Technology",
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                        "goals": ["Learn AI", "Network with professionals"],
                        "interests": ["Machine Learning", "Web Development"],
                        "social_points": 100,
                        "free_requests_remaining": 3,
                        "subscription_tier": "premium",
                        "is_active_in_search": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-05-29T12:00:00Z"
                    }
                }
            }
        },
        404: {"description": "User not found"},
        403: {"description": "Not authorized to access this profile"}
    }
)
async def get_user_profile(
    path_telegram_id: int,
    current_telegram_id: int = Depends(get_current_telegram_id),
    db_client: Client = Depends(get_supabase_client),
    user_service: dict = Depends(get_user_service)
) -> UserResponse:
    """
    Get a user's profile by their Telegram ID.
    
    This endpoint retrieves a user's profile. Users can only access their own profile.
    The user's Telegram ID must be provided in the X-Telegram-Id header.
    
    Args:
        path_telegram_id: Telegram ID of the user to retrieve
        current_telegram_id: Telegram ID from X-Telegram-Id header
        db_client: Supabase client instance
        user_service: User service functions
        
    Returns:
        UserResponse: User profile data
        
    Raises:
        HTTPException: If user not found or not authorized
    """
    # Security check: ensure user can only access their own profile
    if path_telegram_id != current_telegram_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    user = user_service["get_user_profile"](db_client, path_telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {path_telegram_id} not found"
        )
    return user

@router.put(
    "/{path_telegram_id}/profile",
    response_model=UserResponse,
    responses={
        200: {
            "description": "User profile updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "telegram_id": 123456789,
                        "name": "John Doe",
                        "role": "Senior Software Engineer",
                        "industry": "Technology",
                        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                        "goals": ["Learn AI", "Network with professionals", "Start a tech blog"],
                        "interests": ["Machine Learning", "Web Development", "Cloud Computing"],
                        "social_points": 100,
                        "free_requests_remaining": 3,
                        "subscription_tier": "premium",
                        "is_active_in_search": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-05-29T12:00:00Z"
                    }
                }
            }
        },
        404: {"description": "User not found"},
        403: {"description": "Not authorized to update this profile"},
        422: {"description": "Validation error in profile data"}
    }
)
async def update_user_profile(
    path_telegram_id: int,
    profile_data: UserProfileUpdate,
    current_telegram_id: int = Depends(get_current_telegram_id),
    db_client: Client = Depends(get_supabase_client),
    user_service: dict = Depends(get_user_service)
) -> UserResponse:
    """
    Update a user's profile.
    
    This endpoint allows users to update their profile information.
    Users can only update their own profile. The user's Telegram ID must be provided
    in the X-Telegram-Id header.
    
    Args:
        path_telegram_id: Telegram ID of the user to update
        profile_data: UserProfileUpdate model containing fields to update
        current_telegram_id: Telegram ID from X-Telegram-Id header
        db_client: Supabase client instance
        user_service: User service functions
        
    Returns:
        UserResponse: Updated user profile data
        
    Raises:
        HTTPException: If user not found, not authorized, or validation fails
    """
    # Security check: ensure user can only update their own profile
    if path_telegram_id != current_telegram_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    try:
        updated_user = user_service["update_user_profile"](
            db_client=db_client,
            telegram_id=path_telegram_id,
            profile_data_in=profile_data
        )
        return updated_user
    except HTTPException as e:
        # Re-raise HTTP exceptions from service layer
        raise e 