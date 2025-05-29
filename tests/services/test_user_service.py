"""
Unit tests for the user service module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException

from models.user_models import UserCreate, UserProfileUpdate, UserResponse
from services.user_service import UserService
# from app.services.user_service import (
#     get_user_profile_service,
#     create_or_get_user_service,
#     update_user_profile_service
# )
# from app.models.user_models import UserProfileUpdate, UserCreate

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def user_service(mock_user_repo):
    return UserService(mock_user_repo)

@pytest.mark.asyncio
async def test_create_or_get_user_existing(user_service, mock_user_repo):
    # Arrange
    telegram_id = "123456789"
    user_data = UserCreate(
        name="Test User",
        role="Developer",
        industry="Technology",
        skills=["Python", "FastAPI"],
        goals=["Learn AI"],
        interests=["Web Development"]
    )
    existing_user = UserResponse(
        telegram_id=telegram_id,
        name="Test User",
        role="Developer",
        industry="Technology",
        skills=["Python", "FastAPI"],
        goals=["Learn AI"],
        interests=["Web Development"],
        social_points=100,
        free_requests_remaining=5,
        subscription_tier="free",
        is_active_in_search=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repo.get_user_by_telegram_id.return_value = existing_user

    # Act
    result = await user_service.create_or_get_user(telegram_id, user_data)

    # Assert
    assert result == existing_user
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)
    mock_user_repo.create_user.assert_not_called()

@pytest.mark.asyncio
async def test_create_or_get_user_new(user_service, mock_user_repo):
    # Arrange
    telegram_id = "123456789"
    user_data = UserCreate(
        name="Test User",
        role="Developer",
        industry="Technology",
        skills=["Python", "FastAPI"],
        goals=["Learn AI"],
        interests=["Web Development"]
    )
    mock_user_repo.get_user_by_telegram_id.return_value = None
    new_user = UserResponse(
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
    mock_user_repo.create_user.return_value = new_user

    # Act
    result = await user_service.create_or_get_user(telegram_id, user_data)

    # Assert
    assert result == new_user
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)
    mock_user_repo.create_user.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_profile_success(user_service, mock_user_repo):
    # Arrange
    telegram_id = "123456789"
    user = UserResponse(
        telegram_id=telegram_id,
        name="Test User",
        role="Developer",
        industry="Technology",
        skills=["Python", "FastAPI"],
        goals=["Learn AI"],
        interests=["Web Development"],
        social_points=100,
        free_requests_remaining=5,
        subscription_tier="free",
        is_active_in_search=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repo.get_user_by_telegram_id.return_value = user

    # Act
    result = await user_service.get_user_profile(telegram_id)

    # Assert
    assert result == user
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)

@pytest.mark.asyncio
async def test_get_user_profile_not_found(user_service, mock_user_repo):
    # Arrange
    telegram_id = "123456789"
    mock_user_repo.get_user_by_telegram_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match=f"User with telegram_id {telegram_id} not found"):
        await user_service.get_user_profile(telegram_id)
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)

@pytest.mark.asyncio
async def test_update_user_profile_success(user_service, mock_user_repo):
    # Arrange
    telegram_id = "123456789"
    existing_user = UserResponse(
        telegram_id=telegram_id,
        name="Test User",
        role="Developer",
        industry="Technology",
        skills=["Python", "FastAPI"],
        goals=["Learn AI"],
        interests=["Web Development"],
        social_points=100,
        free_requests_remaining=5,
        subscription_tier="free",
        is_active_in_search=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    profile_data = UserProfileUpdate(
        name="Updated Name",
        role="Senior Developer",
        skills=["Python", "FastAPI", "Docker"]
    )
    updated_user = UserResponse(
        telegram_id=telegram_id,
        name=profile_data.name,
        role=profile_data.role,
        industry=existing_user.industry,
        skills=profile_data.skills,
        goals=existing_user.goals,
        interests=existing_user.interests,
        social_points=existing_user.social_points,
        free_requests_remaining=existing_user.free_requests_remaining,
        subscription_tier=existing_user.subscription_tier,
        is_active_in_search=existing_user.is_active_in_search,
        created_at=existing_user.created_at,
        updated_at=datetime.utcnow()
    )
    mock_user_repo.get_user_by_telegram_id.return_value = existing_user
    mock_user_repo.update_user.return_value = updated_user

    # Act
    result = await user_service.update_user_profile(telegram_id, profile_data)

    # Assert
    assert result == updated_user
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)
    mock_user_repo.update_user.assert_called_once()

@pytest.mark.asyncio
async def test_update_user_profile_not_found(user_service, mock_user_repo):
    # Arrange
    telegram_id = "123456789"
    profile_data = UserProfileUpdate(
        name="Updated Name",
        role="Senior Developer"
    )
    mock_user_repo.get_user_by_telegram_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match=f"User with telegram_id {telegram_id} not found"):
        await user_service.update_user_profile(telegram_id, profile_data)
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)
    mock_user_repo.update_user.assert_not_called()

# def test_always_passes():
#     assert True 