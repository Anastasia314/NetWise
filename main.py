"""
Main entry point for the NetWise Telegram bot
"""

import asyncio
import logging
from aiogram import types
from aiogram.filters import Command

from netwise_bot.config import LOG_LEVEL
from netwise_bot.bot_instance import bot, dp

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle the /start command"""
    await message.answer("Hello NetWise!")

async def main():
    """Main function to start the bot"""
    logger.info("Starting NetWise bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 