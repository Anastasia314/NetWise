from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio
import logging
from bot.core.config import get_settings
from bot.handlers.common_handlers import handle_start

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
        
        # Register handlers
        dp.message.register(handle_start, CommandStart())
        logger.info("Handlers registered")
        
        # Start polling
        logger.info("Starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    asyncio.run(main()) 