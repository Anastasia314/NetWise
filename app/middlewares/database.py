from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.db.session import get_supabase_client, get_db_session

class DatabaseMiddleware(BaseMiddleware):
    """Middleware for injecting database clients into handlers"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Get database clients
        db = get_supabase_client()
        session = get_db_session()
        
        try:
            # Add clients to data
            data["db"] = db
            data["session"] = session
            # Call handler
            return await handler(event, data)
        finally:
            # Close session after handler is done
            session.close() 