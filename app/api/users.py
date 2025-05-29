"""
User-related API endpoints.

This module contains all the API endpoints related to user management,
including user onboarding, profile retrieval, and profile updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from models.user_models import UserCreate, UserProfileUpdate, UserResponse
from api.deps import get_supabase_client, get_current_telegram_id, get_user_service
from services.user_service import UserService

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

@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    telegram_id: Annotated[str, Depends(get_current_telegram_id)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """
    Create a new user or get existing user by Telegram ID.
    """
    return await user_service.create_or_get_user(telegram_id, user)

@router.get("/users/me", response_model=UserResponse)
async def get_user_profile(
    telegram_id: Annotated[str, Depends(get_current_telegram_id)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """
    Get current user's profile.
    """
    return await user_service.get_user_profile(telegram_id)

@router.patch("/users/me", response_model=UserResponse)
async def update_user_profile(
    profile: UserProfileUpdate,
    telegram_id: Annotated[str, Depends(get_current_telegram_id)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """
    Update current user's profile.
    """
    return await user_service.update_user_profile(telegram_id, profile) 