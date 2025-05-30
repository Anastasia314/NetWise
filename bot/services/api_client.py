import httpx
import logging
from typing import Dict, Optional
from utils.exceptions import APIClientError, APIClientResponseError

logger = logging.getLogger(__name__)

class APIClient:
    """Client for making requests to the NetWise backend API."""
    
    def __init__(self, base_url: str, timeout: float = 10.0):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the backend API
            timeout: Request timeout in seconds (default: 10.0)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout
        )
        logger.info(f"Initialized APIClient with base URL: {self.base_url}")
    
    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()
        logger.info("Closed APIClient HTTP session")
    
    async def onboard_user(self, telegram_id: int, name: str, username: Optional[str] = None) -> Dict:
        """
        Register a new user with the backend.
        
        Args:
            telegram_id: User's Telegram ID
            name: User's name
            username: Optional Telegram username
            
        Returns:
            Dict containing the user data from the response
            
        Raises:
            APIClientError: For network/connection errors
            APIClientResponseError: For non-2xx HTTP responses
        """
        payload = {
            "telegram_id": str(telegram_id),  # Convert to string as API expects string
            "name": str(name),
            "username": username
        }
        
        try:
            response = await self.client.post(
                "/api/v1/users",
                json=payload,
                headers={"X-Telegram-ID": str(telegram_id)}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Network error during user onboarding: {str(e)}")
            raise APIClientError(f"Failed to connect to API: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"API error during user onboarding: {e.response.status_code} - {e.response.text}")
            raise APIClientResponseError(e.response.status_code, e.response.text)
    
    async def get_user_profile(self, telegram_id: int) -> Dict:
        """
        Fetch a user's profile from the backend.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            Dict containing the user's profile data
            
        Raises:
            APIClientError: For network/connection errors
            APIClientResponseError: For non-2xx HTTP responses
        """
        try:
            response = await self.client.get(
                f"/api/v1/users/me",
                headers={"X-Telegram-ID": str(telegram_id)}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Network error fetching user profile: {str(e)}")
            raise APIClientError(f"Failed to connect to API: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"API error fetching user profile: {e.response.status_code} - {e.response.text}")
            raise APIClientResponseError(e.response.status_code, e.response.text)
    
    async def update_user_profile(self, telegram_id: int, profile_data: Dict) -> Dict:
        """
        Update a user's profile in the backend.
        
        Args:
            telegram_id: User's Telegram ID
            profile_data: Dictionary containing profile update data
            
        Returns:
            Dict containing the updated profile data
            
        Raises:
            APIClientError: For network/connection errors
            APIClientResponseError: For non-2xx HTTP responses
        """
        try:
            response = await self.client.patch(
                f"/api/v1/users/me",
                json=profile_data,
                headers={"X-Telegram-ID": str(telegram_id)}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Network error updating user profile: {str(e)}")
            raise APIClientError(f"Failed to connect to API: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"API error updating user profile: {e.response.status_code} - {e.response.text}")
            raise APIClientResponseError(e.response.status_code, e.response.text) 