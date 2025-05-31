"""
Main entry point for the NetWise Telegram bot
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from netwise_bot.config import LOG_LEVEL, TELEGRAM_BOT_TOKEN
from netwise_bot.handlers import common, profile, connections, requests
from netwise_bot.middleware.activity_middleware import ActivityMiddleware
from netwise_bot.services.user_service import UserService
from netwise_bot.services.graph_service import GraphService
from netwise_bot.services.supabase_client import SupabaseClient
from netwise_bot.services.matching_service import matching_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    try:
        logger.info("Initializing bot...")
        # Initialize bot and dispatcher
        bot = Bot(
            token=TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        logger.info("Bot and dispatcher initialized")
        
        # Initialize services
        logger.info("Initializing services...")
        supabase_client = SupabaseClient()
        user_service = UserService()
        graph_service = GraphService(supabase_client)
        logger.info("Services initialized")
        
        # Register middleware
        logger.info("Registering middleware...")
        dp.update.middleware(ActivityMiddleware(user_service))
        logger.info("Middleware registered")
        
        # Register routers with dependencies
        logger.info("Registering routers...")
        dp.include_router(connections.router)
        dp.include_router(profile.router)
        dp.include_router(common.router)
        dp.include_router(requests.router)
        logger.info("Routers registered")
        
        # Set up dependency injection
        logger.info("Setting up dependency injection...")
        dp["user_service"] = user_service
        dp["graph_service"] = graph_service
        dp["matching_service"] = matching_service
        logger.info("Dependency injection set up")
        
        logger.info("Starting NetWise bot...")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True) 