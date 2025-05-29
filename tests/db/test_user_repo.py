"""
Unit tests for the user repository module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from supabase.client import Client

from models.user_models import UserCreate, UserProfileUpdate, UserResponse
from db.user_repo import UserRepository

@pytest.fixture
def mock_db_client():
    """Fixture providing a mocked Supabase client."""
    return AsyncMock(spec=Client)

@pytest.fixture
def user_repo(mock_db_client):
    """Fixture providing a UserRepository instance with mocked client."""
    return UserRepository(mock_db_client)

@pytest.mark.asyncio
async def test_get_user_by_telegram_id_user_found(user_repo, mock_db_client):
    """Test get_user_by_telegram_id when user is found in database."""
    # Arrange
    telegram_id = "123456789"
    mock_user_data = {
        "telegram_id": telegram_id,
        "name": "Test User",
        "role": "Developer",
        "industry": "Technology",
        "skills": ["Python", "FastAPI"],
        "goals": ["Learn AI"],
        "interests": ["Web Development"],
        "social_points": 100,
        "free_requests_remaining": 5,
        "subscription_tier": "free",
        "subscription_expires_at": None,
        "last_active_at": datetime.now().isoformat(),
        "is_active_in_search": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    
    mock_db_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(return_value=MagicMock(data=mock_user_data))
    
    # Act
    result = await user_repo.get_user_by_telegram_id(telegram_id)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.telegram_id == int(telegram_id)
    assert result.name == mock_user_data["name"]
    assert result.role == mock_user_data["role"]
    assert result.industry == mock_user_data["industry"]
    assert result.skills == mock_user_data["skills"]
    assert result.goals == mock_user_data["goals"]
    assert result.interests == mock_user_data["interests"]
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_db_client.table.return_value.select.assert_called_once_with("*")
    mock_db_client.table.return_value.select.return_value.eq.assert_called_once_with("telegram_id", telegram_id)

@pytest.mark.asyncio
async def test_get_user_by_telegram_id_user_not_found(user_repo, mock_db_client):
    """Test get_user_by_telegram_id when user is not found in database."""
    # Arrange
    telegram_id = "999999999"
    mock_db_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(return_value=MagicMock(data=None))
    
    # Act
    result = await user_repo.get_user_by_telegram_id(telegram_id)
    
    # Assert
    assert result is None
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_db_client.table.return_value.select.assert_called_once_with("*")
    mock_db_client.table.return_value.select.return_value.eq.assert_called_once_with("telegram_id", telegram_id)

@pytest.mark.asyncio
async def test_create_user_success(user_repo, mock_db_client):
    """Test create_user when user is successfully created."""
    # Arrange
    user = UserResponse(
        telegram_id="123456789",
        name="New User",
        role="Developer",
        industry="Technology",
        skills=["Python", "FastAPI"],
        goals=["Learn AI"],
        interests=["Web Development"],
        social_points=0,
        free_requests_remaining=5,
        subscription_tier="free",
        is_active_in_search=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    mock_db_client.table.return_value.insert.return_value.execute = AsyncMock(return_value=MagicMock(data=[user.model_dump()]))
    
    # Act
    result = await user_repo.create_user(user)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.telegram_id == user.telegram_id
    assert result.name == user.name
    assert result.social_points == user.social_points
    assert result.free_requests_remaining == user.free_requests_remaining
    assert result.is_active_in_search == user.is_active_in_search
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_db_client.table.return_value.insert.assert_called_once()

@pytest.mark.asyncio
async def test_update_user_success(user_repo, mock_db_client):
    """Test update_user when profile is successfully updated."""
    # Arrange
    user = UserResponse(
        telegram_id="123456789",
        name="Updated Name",
        role="Senior Developer",
        industry="Technology",
        skills=["Python", "FastAPI", "Docker"],
        goals=["Learn AI"],
        interests=["Web Development"],
        social_points=100,
        free_requests_remaining=5,
        subscription_tier="free",
        is_active_in_search=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    mock_db_client.table.return_value.update.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[user.model_dump()]))
    
    # Act
    result = await user_repo.update_user(user)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.telegram_id == user.telegram_id
    assert result.name == user.name
    assert result.role == user.role
    assert result.skills == user.skills
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_db_client.table.return_value.update.assert_called_once()
    mock_db_client.table.return_value.update.return_value.eq.assert_called_once_with("telegram_id", user.telegram_id) 