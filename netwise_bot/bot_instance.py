"""
Bot instance module for initializing the Telegram bot
"""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import TELEGRAM_BOT_TOKEN

# Export bot and dispatcher classes for use in main.py
__all__ = ['Bot', 'Dispatcher', 'ParseMode', 'DefaultBotProperties', 'MemoryStorage', 'TELEGRAM_BOT_TOKEN']

# Initialize bot and dispatcher
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage) 