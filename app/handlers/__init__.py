from aiogram import Dispatcher
from app.handlers.group_onboarding import router as group_onboarding_router
from app.handlers.profile_creation import router as profile_creation_router

def register_all_handlers(dp: Dispatcher) -> None:
    """Register all handlers."""
    # Register group onboarding handler
    dp.include_router(group_onboarding_router)
    
    # Register profile creation handlers
    dp.include_router(profile_creation_router)
    # Import and register handlers here
    pass 