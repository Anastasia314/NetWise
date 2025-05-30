import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers.user_handlers import (
    handle_start, handle_profile, process_ask_name, process_ask_role,
    process_ask_industry, process_ask_skills, process_ask_goals,
    process_ask_interests, handle_edit_profile_callback, handle_cancel_fsm
)
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

@pytest.fixture
def mock_callback_query():
    """Create a mock CallbackQuery object."""
    callback = MagicMock(spec=CallbackQuery)
    callback.message = MagicMock(spec=Message)
    callback.data = "edit_profile"
    return callback

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

@pytest.mark.asyncio
async def test_process_ask_name(mock_message, mock_state):
    """Test name input processing."""
    mock_message.text = "John Doe"
    
    await process_ask_name(mock_message, mock_state)
    
    # Verify data storage
    mock_state.update_data.assert_called_once_with(name="John Doe")
    
    # Verify state transition
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_ROLE)
    
    # Verify message
    mock_message.answer.assert_called_once()
    assert "role" in mock_message.answer.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_process_ask_role(mock_message, mock_state):
    """Test role input processing."""
    mock_message.text = "Software Engineer"
    
    await process_ask_role(mock_message, mock_state)
    
    mock_state.update_data.assert_called_once_with(role="Software Engineer")
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_INDUSTRY)
    mock_message.answer.assert_called_once()
    assert "industry" in mock_message.answer.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_process_ask_industry(mock_message, mock_state):
    """Test industry input processing."""
    mock_message.text = "Technology"
    
    await process_ask_industry(mock_message, mock_state)
    
    mock_state.update_data.assert_called_once_with(industry="Technology")
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_SKILLS)
    mock_message.answer.assert_called_once()
    assert "skills" in mock_message.answer.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_process_ask_skills(mock_message, mock_state):
    """Test skills input processing."""
    mock_message.text = "Python, JavaScript, Docker"
    
    await process_ask_skills(mock_message, mock_state)
    
    mock_state.update_data.assert_called_once_with(
        skills=["Python", "JavaScript", "Docker"]
    )
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_GOALS)
    mock_message.answer.assert_called_once()
    assert "goals" in mock_message.answer.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_process_ask_goals(mock_message, mock_state):
    """Test goals input processing."""
    mock_message.text = "Learn Rust, Contribute to Open Source"
    
    await process_ask_goals(mock_message, mock_state)
    
    mock_state.update_data.assert_called_once_with(
        goals=["Learn Rust", "Contribute to Open Source"]
    )
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_INTERESTS)
    mock_message.answer.assert_called_once()
    assert "interests" in mock_message.answer.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_process_ask_interests_success(mock_message, mock_state, mock_api_client):
    """Test successful interests processing and profile update."""
    mock_message.text = "AI, Blockchain, Remote Work"
    mock_message.from_user.id = 123456789
    mock_state.get_data.return_value = {
        "name": "John",
        "role": "Developer",
        "industry": "Tech",
        "skills": ["Python"],
        "goals": ["Learn Rust"],
        "interests": ["AI", "Blockchain", "Remote Work"]
    }
    
    await process_ask_interests(mock_message, mock_state, mock_api_client)
    
    # Verify data storage
    mock_state.update_data.assert_called_once_with(
        interests=["AI", "Blockchain", "Remote Work"]
    )
    
    # Verify API call
    mock_api_client.update_user_profile.assert_called_once()
    
    # Verify success message
    mock_message.answer.assert_called_once()
    assert "success" in mock_message.answer.call_args[0][0].lower()
    
    # Verify state clearing
    mock_state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_process_ask_interests_api_error(mock_message, mock_state, mock_api_client):
    """Test interests processing with API error."""
    mock_message.text = "AI, Blockchain"
    mock_api_client.update_user_profile.side_effect = APIClientError("API Error")
    
    await process_ask_interests(mock_message, mock_state, mock_api_client)
    
    # Verify error message
    mock_message.answer.assert_called_once()
    assert "issue" in mock_message.answer.call_args[0][0].lower()
    
    # Verify state clearing
    mock_state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_handle_edit_profile_callback(mock_callback_query, mock_state):
    """Test edit profile callback handler."""
    await handle_edit_profile_callback(mock_callback_query, mock_state)
    
    # Verify callback answer
    mock_callback_query.answer.assert_called_once()
    
    # Verify message
    mock_callback_query.message.answer.assert_called_once()
    assert "name" in mock_callback_query.message.answer.call_args[0][0].lower()
    
    # Verify state transition
    mock_state.set_state.assert_called_once_with(ProfileSetup.ASK_NAME)

@pytest.mark.asyncio
async def test_handle_cancel_fsm_in_state(mock_message, mock_state):
    """Test cancel command when in FSM state."""
    mock_state.get_state.return_value = ProfileSetup.ASK_NAME
    
    await handle_cancel_fsm(mock_message, mock_state)
    
    # Verify message
    mock_message.answer.assert_called_once()
    assert "cancelled" in mock_message.answer.call_args[0][0].lower()
    
    # Verify state clearing
    mock_state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_handle_cancel_fsm_no_state(mock_message, mock_state):
    """Test cancel command when not in FSM state."""
    mock_state.get_state.return_value = None
    
    await handle_cancel_fsm(mock_message, mock_state)
    
    # Verify message
    mock_message.answer.assert_called_once()
    assert "not in any active process" in mock_message.answer.call_args[0][0].lower()
    
    # Verify no state clearing
    mock_state.clear.assert_not_called() 