"""
Main entry point for the NetWise Telegram bot
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

from netwise_bot.config import LOG_LEVEL, get_bot_token
from netwise_bot.bot_instance import bot, dp
from netwise_bot.handlers import common, profile, connections
from netwise_bot.middleware.activity_middleware import ActivityMiddleware
from netwise_bot.services.user_service import UserService
from netwise_bot.services.graph_service import GraphService
from netwise_bot.services.supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    # Initialize bot and dispatcher
    bot = Bot(token=get_bot_token())
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Initialize services
    supabase_client = SupabaseClient()
    user_service = UserService()
    graph_service = GraphService(supabase_client)
    
    # Register middleware
    dp.update.middleware(ActivityMiddleware(user_service))
    
    # Register routers with dependencies
    dp.include_router(common.router)
    dp.include_router(profile.router)
    dp.include_router(connections.router)
    
    # Set up dependency injection
    dp["user_service"] = user_service
    dp["graph_service"] = graph_service
    
    logger.info("Starting NetWise bot...")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 