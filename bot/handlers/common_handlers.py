from aiogram import types
from aiogram.filters import CommandStart

async def handle_start(message: types.Message):
    """Handle the /start command."""
    await message.answer("Welcome to NetWise! I'm here to help you manage your network monitoring tasks.") 