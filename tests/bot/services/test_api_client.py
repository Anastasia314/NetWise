import pytest
import respx
from httpx import Response
from bot.services.api_client import APIClient
from bot.utils.exceptions import APIClientError, APIClientResponseError

@pytest.fixture
def api_client():
    return APIClient(base_url="http://test-api")

@pytest.mark.asyncio
async def test_api_client_initialization():
    """Test that APIClient initializes correctly."""
    client = APIClient(base_url="http://test-api")
    assert client.base_url == "http://test-api"
    assert client.timeout == 10.0
    await client.close()

@pytest.mark.asyncio
async def test_onboard_user_success(api_client):
    """Test successful user onboarding."""
    expected_response = {"id": 1, "telegram_id": 123456, "name": "Test User"}
    
    with respx.mock(base_url="http://test-api") as respx_mock:
        respx_mock.post("/users/onboard").mock(
            return_value=Response(201, json=expected_response)
        )
        
        response = await api_client.onboard_user(
            telegram_id=123456,
            name="Test User",
            username="testuser"
        )
        
        assert response == expected_response
        assert respx_mock.calls.call_count == 1

@pytest.mark.asyncio
async def test_onboard_user_api_error(api_client):
    """Test API error during user onboarding."""
    with respx.mock(base_url="http://test-api") as respx_mock:
        respx_mock.post("/users/onboard").mock(
            return_value=Response(400, text="Invalid request")
        )
        
        with pytest.raises(APIClientResponseError) as exc_info:
            await api_client.onboard_user(
                telegram_id=123456,
                name="Test User"
            )
        
        assert exc_info.value.status_code == 400
        assert "Invalid request" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_user_profile_success(api_client):
    """Test successful profile retrieval."""
    expected_response = {
        "id": 1,
        "telegram_id": 123456,
        "name": "Test User",
        "username": "testuser"
    }
    
    with respx.mock(base_url="http://test-api") as respx_mock:
        respx_mock.get("/users/123456/profile").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await api_client.get_user_profile(telegram_id=123456)
        assert response == expected_response

@pytest.mark.asyncio
async def test_update_user_profile_success(api_client):
    """Test successful profile update."""
    profile_data = {"name": "Updated Name"}
    expected_response = {
        "id": 1,
        "telegram_id": 123456,
        "name": "Updated Name",
        "username": "testuser"
    }
    
    with respx.mock(base_url="http://test-api") as respx_mock:
        respx_mock.put("/users/123456/profile").mock(
            return_value=Response(200, json=expected_response)
        )
        
        response = await api_client.update_user_profile(
            telegram_id=123456,
            profile_data=profile_data
        )
        assert response == expected_response

@pytest.mark.asyncio
async def test_network_error(api_client):
    """Test network error handling."""
    with respx.mock(base_url="http://test-api") as respx_mock:
        respx_mock.get("/users/123456/profile").mock(
            side_effect=Exception("Connection failed")
        )
        
        with pytest.raises(APIClientError) as exc_info:
            await api_client.get_user_profile(telegram_id=123456)
        
        assert "Connection failed" in str(exc_info.value) 