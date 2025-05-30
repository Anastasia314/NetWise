import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User
from aiogram.fsm.context import FSMContext

from bot.handlers.user_handlers import handle_start, handle_profile
from bot.services.api_client import APIClientError
from bot.states.user_states import ProfileSetup

@pytest.fixture
def mock_message():
    """Create a mock Message object."""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 123456789
    message.from_user.first_name = "John"
    message.from_user.username = "john_doe"
    return message

@pytest.fixture
def mock_state():
    """Create a mock FSMContext."""
    state = AsyncMock(spec=FSMContext)
    return state

@pytest.fixture
def mock_api_client():
    """Create a mock APIClient."""
    client = AsyncMock(spec=APIClient)
    return client

@pytest.mark.asyncio
async def test_handle_start_new_user(mock_message, mock_state, mock_api_client):
    """Test /start handler for new user with incomplete profile."""
    # Mock API responses
    mock_api_client.onboard_user.return_value = None
    mock_api_client.get_user_profile.return_value = {
        "name": "John",
        "role": None,
        "industry": None,
        "skills": []
    }
    
    # Call handler
    await handle_start(mock_message, mock_state, mock_api_client)
    
    # Verify API calls
    mock_api_client.onboard_user.assert_called_once_with(
        123456789, "John", "john_doe"
    )
    mock_api_client.get_user_profile.assert_called_once_with(123456789)
    
    # Verify state changes
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_NAME)
    
    # Verify messages sent
    assert mock_message.answer.call_count == 2
    mock_message.answer.assert_any_call(
        "👋 Welcome to NetWise! Let's set up your profile to help you connect with the right people."
    )
    mock_message.answer.assert_any_call(
        "What is your preferred display name?"
    )

@pytest.mark.asyncio
async def test_handle_start_existing_user(mock_message, mock_state, mock_api_client):
    """Test /start handler for existing user with complete profile."""
    # Mock API responses
    mock_api_client.onboard_user.return_value = None
    mock_api_client.get_user_profile.return_value = {
        "name": "John",
        "role": "Developer",
        "industry": "Tech",
        "skills": ["Python"]
    }
    
    # Call handler
    await handle_start(mock_message, mock_state, mock_api_client)
    
    # Verify API calls
    mock_api_client.onboard_user.assert_called_once_with(
        123456789, "John", "john_doe"
    )
    mock_api_client.get_user_profile.assert_called_once_with(123456789)
    
    # Verify state changes
    mock_state.clear.assert_called_once()
    
    # Verify messages sent
    mock_message.answer.assert_called_once_with(
        "👋 Welcome back, John! Here's your main menu:",
        reply_markup=mock_api_client.main_menu_keyboard()
    )

@pytest.mark.asyncio
async def test_handle_start_api_error(mock_message, mock_state, mock_api_client):
    """Test /start handler when API returns an error."""
    # Mock API error
    mock_api_client.onboard_user.side_effect = APIClientError("API Error")
    
    # Call handler
    await handle_start(mock_message, mock_state, mock_api_client)
    
    # Verify error message
    mock_message.answer.assert_called_once_with(
        "😔 Sorry, we're having trouble connecting to our services. Please try again later."
    )

@pytest.mark.asyncio
async def test_handle_profile_success(mock_message, mock_api_client):
    """Test /profile handler with successful profile fetch."""
    # Mock API response
    profile_data = {
        "name": "John",
        "role": "Developer",
        "industry": "Tech",
        "skills": ["Python"],
        "goals": ["Learn Rust"],
        "interests": ["AI"],
        "social_points": 100
    }
    mock_api_client.get_user_profile.return_value = profile_data
    
    # Call handler
    await handle_profile(mock_message, mock_api_client)
    
    # Verify API call
    mock_api_client.get_user_profile.assert_called_once_with(123456789)
    
    # Verify message sent
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[1]
    assert "parse_mode" in call_args
    assert call_args["parse_mode"] == "MarkdownV2"
    assert "reply_markup" in call_args

@pytest.mark.asyncio
async def test_handle_profile_api_error(mock_message, mock_api_client):
    """Test /profile handler when API returns an error."""
    # Mock API error
    mock_api_client.get_user_profile.side_effect = APIClientError("API Error")
    
    # Call handler
    await handle_profile(mock_message, mock_api_client)
    
    # Verify error message
    mock_message.answer.assert_called_once_with(
        "😔 Sorry, we couldn't fetch your profile. Please try again later."
    ) 