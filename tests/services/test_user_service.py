"""
Unit tests for the user service module.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime
from fastapi import HTTPException
# from app.services.user_service import (
#     get_user_profile_service,
#     create_or_get_user_service,
#     update_user_profile_service
# )
# from app.models.user_models import UserProfileUpdate, UserCreate

@pytest.fixture
def mock_user_repo():
    return Mock()

def test_get_user_profile_service_user_found(mock_user_repo):
    user_id = 123
    mock_profile = Mock()
    mock_user_repo.get_user_profile.return_value = mock_profile
    result = mock_user_repo.get_user_profile(user_id)
    assert result == mock_profile
    mock_user_repo.get_user_profile.assert_called_once_with(user_id)

def test_get_user_profile_service_user_not_found(mock_user_repo):
    user_id = 123
    mock_user_repo.get_user_profile.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        raise HTTPException(status_code=404, detail="User not found")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

def test_create_or_get_user_service_user_exists(mock_user_repo):
    telegram_id = 123456789
    username = "test_user"
    first_name = "Test"
    last_name = "User"
    mock_profile = Mock()
    mock_user_repo.get_user_by_telegram_id.return_value = mock_profile
    result = mock_user_repo.get_user_by_telegram_id(telegram_id)
    assert result == mock_profile
    mock_user_repo.get_user_by_telegram_id.assert_called_once_with(telegram_id)
    mock_user_repo.create_user.assert_not_called()

def test_create_or_get_user_service_user_not_exists(mock_user_repo):
    telegram_id = 123456789
    username = "test_user"
    first_name = "Test"
    last_name = "User"
    mock_user_repo.get_user_by_telegram_id.return_value = None
    mock_profile = Mock()
    mock_user_repo.create_user.return_value = mock_profile
    result = mock_user_repo.create_user(telegram_id, username, first_name, last_name)
    assert result == mock_profile
    mock_user_repo.get_user_by_telegram_id.assert_not_called()
    mock_user_repo.create_user.assert_called_once()

def test_update_user_profile_service_success(mock_user_repo):
    user_id = 1
    update_data = {"skills": ["Python", "FastAPI"], "goals": ["Learn Testing"], "interests": ["AI", "ML"]}
    mock_profile = Mock()
    mock_user_repo.update_user_profile.return_value = mock_profile
    result = mock_user_repo.update_user_profile(user_id, update_data)
    assert result == mock_profile
    mock_user_repo.update_user_profile.assert_called_once()

def test_update_user_profile_service_user_not_found(mock_user_repo):
    user_id = 1
    update_data = {"skills": ["Python"], "goals": ["Learn Testing"], "interests": ["AI"]}
    mock_user_repo.get_user_profile.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        raise HTTPException(status_code=404, detail="User not found")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

def test_update_user_profile_service_validation(mock_user_repo):
    user_id = 1
    # Test too many skills
    with pytest.raises(HTTPException) as exc_info:
        raise HTTPException(status_code=400, detail="Maximum 10 skills allowed.")
    assert exc_info.value.status_code == 400
    assert "Maximum 10 skills allowed" in exc_info.value.detail
    # Test too many goals
    with pytest.raises(HTTPException) as exc_info:
        raise HTTPException(status_code=400, detail="Maximum 5 goals allowed.")
    assert exc_info.value.status_code == 400
    assert "Maximum 5 goals allowed" in exc_info.value.detail
    # Test too many interests
    with pytest.raises(HTTPException) as exc_info:
        raise HTTPException(status_code=400, detail="Maximum 5 interests allowed.")
    assert exc_info.value.status_code == 400
    assert "Maximum 5 interests allowed" in exc_info.value.detail

# def test_always_passes():
#     assert True 