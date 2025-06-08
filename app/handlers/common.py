from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("ping"))
async def cmd_ping(message: types.Message):
    """Handle /ping command - simple health check."""
    await message.answer("🏓 Pong!") 