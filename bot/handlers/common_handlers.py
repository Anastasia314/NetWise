from aiogram import types
from aiogram.filters import CommandStart
import logging

logger = logging.getLogger(__name__)

async def handle_start(message: types.Message, api_client):
    """Handle the /start command."""
    try:
        # Register user with the backend
        user_data = await api_client.onboard_user(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            username=message.from_user.username
        )
        
        # Send welcome message
        await message.answer(
            f"Welcome to NetWise, {message.from_user.full_name}! "
            "I'm here to help you manage your network monitoring tasks."
        )
    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        await message.answer("Sorry, there was an error. Please try again later.") 