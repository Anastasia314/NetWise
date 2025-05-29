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
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/onboard", response_model=UserResponse)
async def onboard_user(
    name: Optional[str] = None,
    username: Optional[str] = None,
    telegram_id: int = Depends(get_current_telegram_id),
    db_client: Client = Depends(get_supabase_client),
    user_service: dict = Depends(get_user_service)
) -> UserResponse:
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

@router.get("/{path_telegram_id}/profile", response_model=UserResponse)
async def get_user_profile(
    path_telegram_id: int,
    current_telegram_id: int = Depends(get_current_telegram_id),
    db_client: Client = Depends(get_supabase_client),
    user_service: dict = Depends(get_user_service)
) -> UserResponse:
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

@router.put("/{path_telegram_id}/profile", response_model=UserResponse)
async def update_user_profile(
    path_telegram_id: int,
    profile_data: UserProfileUpdate,
    current_telegram_id: int = Depends(get_current_telegram_id),
    db_client: Client = Depends(get_supabase_client),
    user_service: dict = Depends(get_user_service)
) -> UserResponse:
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