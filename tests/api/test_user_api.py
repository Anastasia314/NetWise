"""
Integration tests for user API endpoints.

Этот модуль содержит интеграционные тесты для API пользователей,
используя dependency override и мок-объекты для сервисного слоя.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.main import app
from app.models.user_models import UserResponse, UserProfileUpdate
from app.api.deps import get_user_service, get_current_telegram_id, get_supabase_client

client = TestClient(app)

# Тестовые данные
TEST_TELEGRAM_ID = 123456789
TEST_NAME = "Test User"
TEST_USERNAME = "testuser"
OTHER_TELEGRAM_ID = 987654321
UPDATED_NAME = "Updated User"
UPDATED_ROLE = "Senior Developer"

@pytest.fixture
def mock_user_service():
    """Fixture providing a mocked user service."""
    mock = Mock()
    app.dependency_overrides[get_user_service] = lambda: {
        "create_or_get_user": mock.create_or_get_user_service,
        "get_user_profile": mock.get_user_profile_service,
        "update_user_profile": mock.update_user_profile_service
    }
    yield mock
    app.dependency_overrides.clear()

@pytest.fixture
def mock_telegram_id():
    """Fixture providing a mocked telegram ID dependency."""
    app.dependency_overrides[get_current_telegram_id] = lambda: TEST_TELEGRAM_ID
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def mock_supabase_client():
    """Fixture providing a mocked Supabase client."""
    mock = Mock()
    app.dependency_overrides[get_supabase_client] = lambda: mock
    yield mock
    app.dependency_overrides.clear()

def test_app_initialization():
    """Test that the FastAPI app is properly initialized."""
    assert app is not None
    assert app.title == "NetWise API"
    assert app.version == "0.1.0"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "environment" in data
    assert "version" in data

def test_onboard_new_user(mock_user_service, mock_telegram_id, mock_supabase_client):
    """Test onboarding a new user."""
    mock_user = UserResponse(
        telegram_id=TEST_TELEGRAM_ID,
        name=TEST_NAME,
        created_at=datetime.now(),
        updated_at=datetime.now() + timedelta(seconds=1)  # Different timestamps for new user
    )
    mock_user_service.create_or_get_user_service.return_value = mock_user
    response = client.post(
        "/users/onboard",
        headers={"X-Telegram-Id": str(TEST_TELEGRAM_ID)},
        json={"name": TEST_NAME}
    )
    assert response.status_code == 201
    assert response.json()["telegram_id"] == TEST_TELEGRAM_ID
    assert response.json()["name"] == TEST_NAME
    mock_user_service.create_or_get_user_service.assert_called_once()

def test_onboard_existing_user(mock_user_service, mock_telegram_id, mock_supabase_client):
    """Test onboarding an existing user."""
    mock_user = UserResponse(
        telegram_id=TEST_TELEGRAM_ID,
        name=TEST_NAME,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1)  # Same timestamps for existing user
    )
    mock_user_service.create_or_get_user_service.return_value = mock_user
    response = client.post(
        "/users/onboard",
        headers={"X-Telegram-Id": str(TEST_TELEGRAM_ID)},
        json={"name": TEST_NAME}
    )
    assert response.status_code == 200
    assert response.json()["telegram_id"] == TEST_TELEGRAM_ID
    assert response.json()["name"] == TEST_NAME
    mock_user_service.create_or_get_user_service.assert_called_once()

def test_get_user_profile_found(mock_user_service, mock_telegram_id, mock_supabase_client):
    """Test getting a user's profile when user exists."""
    mock_user = UserResponse(
        telegram_id=TEST_TELEGRAM_ID,
        name=TEST_NAME,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1)
    )
    mock_user_service.get_user_profile_service.return_value = mock_user
    response = client.get(
        f"/users/{TEST_TELEGRAM_ID}/profile",
        headers={"X-Telegram-Id": str(TEST_TELEGRAM_ID)}
    )
    assert response.status_code == 200
    assert response.json()["telegram_id"] == TEST_TELEGRAM_ID
    assert response.json()["name"] == TEST_NAME
    mock_user_service.get_user_profile_service.assert_called_once() 