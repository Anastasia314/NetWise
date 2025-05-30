from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from ..services.user_service import UserService

class ActivityTrackingMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        """
        Initialize the activity tracking middleware.
        
        Args:
            user_service (UserService): The user service instance
        """
        self.user_service = user_service
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process the event and update user activity.
        
        Args:
            handler (Callable): The handler function
            event (TelegramObject): The event object
            data (Dict[str, Any]): Additional data
            
        Returns:
            Any: The result of the handler
        """
        # Get user ID from the event
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif hasattr(event, 'callback_query') and event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id

        # Update user activity if we have a user ID
        if user_id:
            self.user_service.update_last_active(user_id)

        # Call the next handler
        return await handler(event, data) 