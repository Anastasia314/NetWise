from aiogram import Dispatcher
from app.handlers.common import router as common_router

def register_all_handlers(dp: Dispatcher) -> None:
    """Register all handlers."""
    dp.include_router(common_router)
    # Import and register handlers here
    pass 