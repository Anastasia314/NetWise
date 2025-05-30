"""
API client for making HTTP requests to external services.
"""

import aiohttp
from typing import Optional, Dict, Any
from ..utils.exceptions import APIClientError, APIClientResponseError

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Request headers
            
        Returns:
            Dict containing the response data
            
        Raises:
            APIClientError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        session = await self._get_session()
        
        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            ) as response:
                response_data = await response.json()
                
                if not response.ok:
                    raise APIClientResponseError(
                        status_code=response.status,
                        message=response_data.get('detail', 'Unknown error')
                    )
                    
                return response_data
        except aiohttp.ClientError as e:
            raise APIClientError(f"Request failed: {str(e)}")
        except Exception as e:
            raise APIClientError(f"Unexpected error: {str(e)}") 