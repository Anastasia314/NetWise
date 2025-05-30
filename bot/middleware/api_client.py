"""
Middleware for injecting API client into handlers.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from services.api_client import APIClient

class APIClientMiddleware(BaseMiddleware):
    """Middleware that injects API client into handler context."""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Inject API client into handler context
        data["api_client"] = self.api_client
        return await handler(event, data) 