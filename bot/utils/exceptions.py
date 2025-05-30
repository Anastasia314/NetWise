class APIClientError(Exception):
    """Base exception for API client errors."""
    pass

class APIClientResponseError(APIClientError):
    """Exception raised for non-2xx HTTP responses."""
    def __init__(self, status_code: int, response_content: str):
        self.status_code = status_code
        self.response_content = response_content
        super().__init__(f"API request failed with status {status_code}: {response_content}") 