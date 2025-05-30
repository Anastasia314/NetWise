"""
Main entry point for the NetWise Telegram bot
"""

import asyncio
import logging
from aiogram import types
from aiogram.filters import Command

from netwise_bot.config import LOG_LEVEL
from netwise_bot.bot_instance import bot, dp
from netwise_bot.handlers import common, profile
from netwise_bot.middleware.activity_middleware import ActivityTrackingMiddleware
from netwise_bot.services.user_service import UserService

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    logger.info("Starting NetWise bot...")
    
    # Initialize services
    user_service = UserService()
    
    # Register middleware
    dp.update.middleware(ActivityTrackingMiddleware(user_service))
    
    # Register routers
    dp.include_router(common.router)
    dp.include_router(profile.router)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 