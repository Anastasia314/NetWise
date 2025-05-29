"""
User service module.

This module contains service functions for user management,
including user profile retrieval, creation, and updates.
"""

from typing import Optional
from datetime import datetime
from supabase.client import Client

from models.user_models import UserCreate, UserProfileUpdate, UserResponse
from db.user_repo import UserRepository

# Constants for validation
MAX_SKILLS = 10
MAX_GOALS = 5
MAX_INTERESTS = 5

class UserService:
    def __init__(self, db_client: Client):
        self.user_repo = UserRepository(db_client)

    async def create_or_get_user(self, telegram_id: str, user_data: UserCreate) -> UserResponse:
        """
        Create a new user or get existing user by Telegram ID.
        """
        existing_user = await self.user_repo.get_user_by_telegram_id(telegram_id)
        if existing_user:
            return existing_user

        user = UserResponse(
            telegram_id=telegram_id,
            name=user_data.name,
            role=user_data.role,
            industry=user_data.industry,
            skills=user_data.skills,
            goals=user_data.goals,
            interests=user_data.interests,
            social_points=0,
            free_requests_remaining=5,
            subscription_tier="free",
            is_active_in_search=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self.user_repo.create_user(user)

    async def get_user_profile(self, telegram_id: str) -> UserResponse:
        """
        Get user profile by Telegram ID.
        """
        user = await self.user_repo.get_user_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id {telegram_id} not found")
        return user

    async def update_user_profile(self, telegram_id: str, profile_data: UserProfileUpdate) -> UserResponse:
        """
        Update user profile.
        """
        user = await self.user_repo.get_user_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        update_data = profile_data.model_dump(exclude_unset=True)
        updated_user = user.model_copy(update=update_data)
        updated_user.updated_at = datetime.utcnow()

        return await self.user_repo.update_user(updated_user)