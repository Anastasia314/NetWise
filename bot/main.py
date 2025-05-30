from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio
import logging
import os
from dotenv import load_dotenv
from core.config import get_settings, Config
from handlers.common_handlers import handle_start
from services.api_client import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize dispatcher
dp = Dispatcher()

async def main():
    try:
        # Get settings
        settings = get_settings()
        logger.info("Settings loaded successfully")
        
        # Initialize bot with token from settings
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        logger.info("Bot initialized")
        
        # Initialize API client
        api_client = APIClient(base_url=Config.API_BASE_URL)
        logger.info(f"API client initialized with base URL: {Config.API_BASE_URL}")
        
        # Make API client available to handlers through bot's context
        bot["api_client"] = api_client
        
        # Register handlers
        dp.message.register(handle_start, CommandStart())
        logger.info("Handlers registered")
        
        # Start polling
        logger.info("Starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise
    finally:
        # Clean up resources
        if "api_client" in bot:
            await bot["api_client"].close()
            logger.info("API client closed")

if __name__ == '__main__':
    asyncio.run(main()) 