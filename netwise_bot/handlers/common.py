from aiogram import Router, types, F
from aiogram.filters import Command
from ..services.user_service import UserService
from ..keyboards.common_keyboards import get_initial_setup_keyboard, get_main_menu_keyboard, get_search_settings_keyboard

# Create router for common handlers
router = Router()

# Initialize UserService
user_service = UserService()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Handle the /start command.
    
    Args:
        message (types.Message): The message object
    """
    # Get or create user
    user = user_service.get_or_create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name
    )
    
    if not user:
        await message.answer("Sorry, there was an error processing your request. Please try again later.")
        return
    
    # Send welcome message
    await message.answer(
        f"Welcome to NetWise, {user['name']}! 🎉\n\n"
        "I'm here to help you connect with other professionals and grow your network.\n\n"
        "Use the menu below to get started:",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Handle the /help command.
    
    Args:
        message (types.Message): The message object
    """
    help_text = (
        "Here's how to use NetWise:\n\n"
        "1. Create your profile using the 'Create Profile' button\n"
        "2. Set your visibility in search using the 'Search Settings' button\n"
        "3. Find connections using the 'Find Connections' button\n"
        "4. View your profile using the 'My Profile' button\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/myprofile - View your profile\n"
        "/cancel - Cancel any ongoing operation"
    )
    await message.answer(help_text)

@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    """
    Handle the /cancel command.
    
    Args:
        message (types.Message): The message object
    """
    await message.answer(
        "Operation cancelled. You can start a new operation using the menu below:",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(F.text == "🔍 Search Settings")
async def handle_search_settings(message: types.Message):
    """
    Handle the search settings button click.
    
    Args:
        message (types.Message): The message object
    """
    user = user_service.get_profile(message.from_user.id)
    if not user:
        await message.answer("Please create your profile first using the 'Create Profile' button.")
        return
    
    current_status = "visible" if user.get('is_active_in_search', True) else "hidden"
    await message.answer(
        f"Your profile is currently {current_status} in search.\n\n"
        "Would you like to change this?",
        reply_markup=get_search_settings_keyboard()
    )

@router.callback_query(F.data.startswith("search_"))
async def handle_search_settings_callback(callback: types.CallbackQuery):
    """
    Handle search settings callback queries.
    
    Args:
        callback (types.CallbackQuery): The callback query object
    """
    action = callback.data.split("_")[1]
    
    if action == "show":
        success = user_service.set_search_status(callback.from_user.id, True)
        if success:
            await callback.message.edit_text("Your profile is now visible in search.")
        else:
            await callback.message.edit_text("Failed to update search settings. Please try again.")
    
    elif action == "hide":
        success = user_service.set_search_status(callback.from_user.id, False)
        if success:
            await callback.message.edit_text("Your profile is now hidden from search.")
        else:
            await callback.message.edit_text("Failed to update search settings. Please try again.")
    
    await callback.answer() 