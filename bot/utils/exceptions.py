"""
Custom exceptions for the bot application.
"""

class APIClientError(Exception):
    """Base exception for API client errors."""
    pass

class APIClientResponseError(APIClientError):
    """Exception raised when API client receives an error response."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API request failed with status {status_code}: {message}") 