"""
Unit tests for the user repository module.
"""

import pytest
from unittest.mock import Mock, patch
from supabase import Client
from datetime import datetime
from postgrest.exceptions import APIError

from app.db.user_repo import get_user_by_telegram_id, create_user, update_user_profile
from app.models.user_models import UserCreate, UserProfileUpdate, UserResponse


@pytest.fixture
def mock_db_client():
    """Fixture providing a mocked Supabase client."""
    return Mock(spec=Client)


def test_get_user_by_telegram_id_user_found(mock_db_client):
    """Test get_user_by_telegram_id when user is found in database."""
    # Arrange
    telegram_id = 123456789
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
    
    # Mock the Supabase client's table().select().eq().execute() chain
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_db_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.execute.return_value.data = [mock_user_data]
    
    # Act
    result = get_user_by_telegram_id(mock_db_client, telegram_id)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.telegram_id == telegram_id
    assert result.name == mock_user_data["name"]
    assert result.role == mock_user_data["role"]
    assert result.industry == mock_user_data["industry"]
    assert result.skills == mock_user_data["skills"]
    assert result.goals == mock_user_data["goals"]
    assert result.interests == mock_user_data["interests"]
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_table.select.assert_called_once_with("*")
    mock_select.eq.assert_called_once_with("telegram_id", telegram_id)
    mock_eq.execute.assert_called_once()


def test_get_user_by_telegram_id_user_not_found(mock_db_client):
    """Test get_user_by_telegram_id when user is not found in database."""
    # Arrange
    telegram_id = 999999999
    
    # Mock the Supabase client's table().select().eq().execute() chain
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_db_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.execute.return_value.data = []  # Empty list indicates no user found
    
    # Act
    result = get_user_by_telegram_id(mock_db_client, telegram_id)
    
    # Assert
    assert result is None
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_table.select.assert_called_once_with("*")
    mock_select.eq.assert_called_once_with("telegram_id", telegram_id)
    mock_eq.execute.assert_called_once()


def test_create_user_success(mock_db_client):
    """Test create_user when user is successfully created."""
    # Arrange
    telegram_id = 123456789
    name = "New User"
    role = "Developer"
    industry = "Technology"
    skills = ["Python", "FastAPI"]
    goals = ["Learn AI"]
    interests = ["Web Development"]
    
    # Mock the response data that would be returned from Supabase
    mock_response_data = {
        "telegram_id": telegram_id,
        "name": name,
        "role": role,
        "industry": industry,
        "skills": skills,
        "goals": goals,
        "interests": interests,
        "social_points": 0,
        "free_requests_remaining": 5,
        "subscription_tier": None,
        "subscription_expires_at": None,
        "last_active_at": None,
        "is_active_in_search": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    
    # Mock the Supabase client's table().insert().execute() chain
    mock_table = Mock()
    mock_insert = Mock()
    mock_db_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value.data = [mock_response_data]
    
    # Act
    result = create_user(mock_db_client, telegram_id, name)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.telegram_id == telegram_id
    assert result.name == name
    assert result.social_points == 0
    assert result.free_requests_remaining == 5
    assert result.is_active_in_search is True
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_table.insert.assert_called_once()
    mock_insert.execute.assert_called_once()


def test_create_user_duplicate_telegram_id(mock_db_client):
    """Test create_user when attempting to create a user with a duplicate telegram_id."""
    # Arrange
    telegram_id = 123456789
    name = "New User"
    
    # Mock the Supabase client to raise an APIError for duplicate key violation
    mock_table = Mock()
    mock_insert = Mock()
    mock_db_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.side_effect = APIError({
        "message": "duplicate key value violates unique constraint",
        "code": "23505"
    })
    
    # Act & Assert
    with pytest.raises(APIError) as exc_info:
        create_user(mock_db_client, telegram_id, name)
    
    # Verify the error details
    assert "duplicate key value" in str(exc_info.value)
    assert exc_info.value.code == "23505"
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_table.insert.assert_called_once()
    mock_insert.execute.assert_called_once()


def test_update_user_profile_success(mock_db_client):
    """Test update_user_profile when profile is successfully updated."""
    # Arrange
    telegram_id = 123456789
    profile_data = UserProfileUpdate(
        name="Updated Name",
        role="Senior Developer",
        skills=["Python", "FastAPI", "Docker"]  # Only updating a subset of fields
    )
    
    # Mock the response data that would be returned from Supabase
    mock_response_data = {
        "telegram_id": telegram_id,
        "name": profile_data.name,
        "role": profile_data.role,
        "industry": "Technology",  # Unchanged field
        "skills": profile_data.skills,
        "goals": ["Learn AI"],  # Unchanged field
        "interests": ["Web Development"],  # Unchanged field
        "social_points": 100,  # Unchanged field
        "free_requests_remaining": 5,  # Unchanged field
        "subscription_tier": "free",  # Unchanged field
        "subscription_expires_at": None,  # Unchanged field
        "last_active_at": datetime.now().isoformat(),  # Unchanged field
        "is_active_in_search": True,  # Unchanged field
        "created_at": datetime.now().isoformat(),  # Unchanged field
        "updated_at": datetime.now().isoformat()  # Updated timestamp
    }
    
    # Mock the Supabase client's table().update().eq().execute() chain
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_db_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_eq.execute.return_value.data = [mock_response_data]
    
    # Act
    result = update_user_profile(mock_db_client, telegram_id, profile_data.model_dump(exclude_unset=True))
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    assert result.telegram_id == telegram_id
    assert result.name == profile_data.name
    assert result.role == profile_data.role
    assert result.skills == profile_data.skills
    # Verify unchanged fields remain the same
    assert result.industry == "Technology"
    assert result.goals == ["Learn AI"]
    assert result.interests == ["Web Development"]
    assert result.social_points == 100
    assert result.free_requests_remaining == 5
    assert result.subscription_tier == "free"
    assert result.is_active_in_search is True
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_table.update.assert_called_once()
    mock_update.eq.assert_called_once_with("telegram_id", telegram_id)
    mock_eq.execute.assert_called_once()


def test_update_user_profile_user_not_found(mock_db_client):
    """Test update_user_profile when user is not found in database."""
    # Arrange
    telegram_id = 999999999
    profile_data = UserProfileUpdate(
        name="Updated Name",
        role="Senior Developer"
    )
    
    # Mock the Supabase client's table().update().eq().execute() chain
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_db_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_eq.execute.return_value.data = []  # Empty list indicates no user found
    
    # Act
    result = update_user_profile(mock_db_client, telegram_id, profile_data.model_dump(exclude_unset=True))
    
    # Assert
    assert result is None
    
    # Verify the correct chain of calls was made
    mock_db_client.table.assert_called_once_with("users")
    mock_table.update.assert_called_once()
    mock_update.eq.assert_called_once_with("telegram_id", telegram_id)
    mock_eq.execute.assert_called_once() 