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

from netwise_bot.config import LOG_LEVEL, TELEGRAM_BOT_TOKEN, load_config
from netwise_bot.handlers import common, profile, connections, requests, interactions
from netwise_bot.middleware.activity_middleware import ActivityMiddleware
from netwise_bot.services.user_service import user_service
from netwise_bot.services.graph_service import GraphService
from netwise_bot.services.supabase_client import SupabaseClient
from netwise_bot.services.matching_service import matching_service
from netwise_bot.scheduler import scheduler_manager
from netwise_bot.services.notification_service import NotificationService
from netwise_bot.services.request_service import request_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def send_daily_digests():
    """Send daily digests to all active users."""
    try:
        # Get all active users
        response = await user_service.supabase.table('users').select('telegram_id').eq('is_active_in_search', True).execute()
        users = response.data
        
        for user in users:
            await notification_service.send_daily_digest(user['telegram_id'])
            
    except Exception as e:
        logger.error(f"Error sending daily digests: {e}")

async def manage_inactive_users():
    """Manage inactive users by sending reminders and deactivating them."""
    try:
        # Send reminders to users approaching inactivity
        await notification_service.send_inactive_reminders()
        
        # Deactivate users who have been inactive for too long
        deactivated_count = await user_service.deactivate_inactive_users()
        if deactivated_count > 0:
            logger.info(f"Deactivated {deactivated_count} inactive users")
            
    except Exception as e:
        logger.error(f"Error managing inactive users: {e}")

async def main():
    """Main function to start the bot"""
    try:
        logger.info("Initializing bot...")
        # Load configuration
        config = load_config()
        
        # Initialize bot and dispatcher
        bot = Bot(
            token=config.telegram_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        logger.info("Bot and dispatcher initialized")
        
        # Initialize services
        logger.info("Initializing services...")
        supabase_client = SupabaseClient()
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
        dp.include_router(interactions.router)
        logger.info("Routers registered")
        
        # Set up dependency injection
        logger.info("Setting up dependency injection...")
        dp["user_service"] = user_service
        dp["graph_service"] = graph_service
        dp["matching_service"] = matching_service
        logger.info("Dependency injection set up")
        
        # Initialize and start scheduler
        scheduler_manager.init_scheduler()
        scheduler_manager.add_daily_job(send_daily_digests, hour=9, minute=0)
        scheduler_manager.add_daily_job(manage_inactive_users, hour=0, minute=0)
        scheduler_manager.start()
        
        # Create notification_service instance
        notification_service = NotificationService(bot, request_service, user_service)
        dp["notification_service"] = notification_service
        
        logger.info("Starting NetWise bot...")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise
    finally:
        # Shutdown scheduler
        scheduler_manager.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True) 