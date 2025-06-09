from aiogram import Dispatcher, Router
from app.handlers.group_onboarding import router as group_onboarding_router
from app.handlers.profile_creation import router as profile_creation_router
from app.handlers.search import router as search_router
from app.handlers.help import router as help_router
from app.handlers.profile_management import router as profile_management_router

def register_all_handlers(dp: Dispatcher) -> None:
    """Register all handlers."""
    # Register search router first to handle pagination
    dp.include_router(search_router)
    
    # Register other handlers
    dp.include_router(group_onboarding_router)
    dp.include_router(profile_creation_router)
    dp.include_router(help_router)
    dp.include_router(profile_management_router) 