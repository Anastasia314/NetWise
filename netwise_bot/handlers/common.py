from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
import logging
from ..services.user_service import UserService
from ..services.graph_service import GraphService
from ..keyboards.common_keyboards import get_initial_setup_keyboard, get_search_settings_keyboard
from ..states.profile_states import ProfileStates
from ..handlers.profile import show_profile
from ..handlers.requests import cmd_newrequest
from ..keyboards.main_menu import get_main_menu_keyboard, get_profile_menu_keyboard, get_main_menu_inline_keyboard, get_menu_button
from ..states.request_states import RequestStates

# Create router for common handlers
router = Router()

# Initialize UserService
user_service = UserService()

# Get logger
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def handle_start(
    message: types.Message,
    state: FSMContext,
    user_service: UserService = None,
    graph_service: GraphService = None
):
    """Handle /start command."""
    try:
        logger.info(f"Processing /start command for user {message.from_user.id}")
        
        # Get or create user
        user = await user_service.get_or_create_user(
            message.from_user.id,
            message.from_user.full_name
        )
        
        if not user:
            logger.error(f"Failed to create user for {message.from_user.id}")
            await message.answer(
                "Welcome to NetWise! There was an error creating your account. "
                "Please try again later."
            )
            return
        
        # Check if user has a profile
        profile = await user_service.get_profile(message.from_user.id)
        logger.info(f"User profile status: {'exists' if profile else 'not found'}")
        
        # Сначала отправляем приветствие
        await message.answer("👋 Welcome to NetWise!", reply_markup=get_menu_button())
        
        if not profile:
            # New user without profile
            logger.info(f"New user {message.from_user.id} - showing initial setup")
            await message.answer(
                "Let's create your professional profile to help you "
                "connect with the right people.",
                reply_markup=get_initial_setup_keyboard()
            )
        else:
            # Existing user with profile
            logger.info(f"Existing user {message.from_user.id} - showing profile menu")
            await message.answer(
                f"Welcome back, {profile.get('name', 'there')}! What would you like to do?",
                reply_markup=get_profile_menu_keyboard()
            )
        
        # Добавляем кнопку меню в нижнюю панель
    except Exception as e:
        logger.error(f"Error in handle_start: {e}", exc_info=True)
        await message.answer(
            "Sorry, there was an error processing your request. "
            "Please try again later."
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

@router.callback_query(F.data == "create_profile")
async def process_create_profile_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Let's create your profile! Use /myprofile to view or edit your profile.")

@router.callback_query(F.data == "view_profile")
async def process_view_profile_callback(callback: types.CallbackQuery):
    await callback.answer()
    await show_profile(callback.message, telegram_id=callback.from_user.id)

@router.callback_query(F.data == "edit_profile")
async def process_edit_profile_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileStates.name)
    await callback.message.answer("Let's update your profile! What's your name or preferred display name?")

@router.callback_query(lambda c: c.data == "profile_view")
async def handle_profile_view(callback: types.CallbackQuery):
    await show_profile(callback.message, telegram_id=callback.from_user.id)
    await callback.answer()

@router.callback_query(lambda c: c.data == "profile_edit")
async def handle_profile_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Let's update your profile! What's your name or preferred display name?")
    await state.set_state(ProfileStates.name)
    await callback.answer()

@router.message(lambda m: m.text == "Generate Invite")
async def handle_generate_invite_menu(message: types.Message):
    # Триггерим колбэк generate_invite
    fake_callback = types.CallbackQuery(
        id="menu_fake_invite",
        from_user=message.from_user,
        message=message,
        data="generate_invite"
    )
    await generate_invite_link(fake_callback)

@router.message(lambda m: m.text == "Toggle Search")
async def handle_toggle_search_menu(message: types.Message):
    # Триггерим колбэк toggle_search (реализуйте обработчик отдельно)
    fake_callback = types.CallbackQuery(
        id="menu_fake_toggle_search",
        from_user=message.from_user,
        message=message,
        data="toggle_search"
    )
    # Если есть обработчик toggle_search, вызовите его здесь
    # await handle_toggle_search(fake_callback)
    await message.answer("🔍 Search toggled (stub handler)")

@router.message(Command("myprofile"))
async def cmd_myprofile(message: types.Message):
    """Handle /myprofile command."""
    await show_profile(message, telegram_id=message.from_user.id)

@router.callback_query(F.data == "help")
async def handle_help_callback(callback: types.CallbackQuery):
    """Handle help button click."""
    help_text = (
        "Need help with NetWise? Here's what you can do:\n\n"
        "1. Check your profile and connections\n"
        "2. Generate invite links for new connections\n"
        "3. Toggle your visibility in search\n\n"
        "If you encounter any issues or have questions, "
        "please contact us at:\n"
        "📧 kodable.pro.info@gmail.com"
    )
    await callback.message.answer(help_text)
    await callback.answer()

@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Handle /menu command."""
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_inline_keyboard()
    )

@router.callback_query(F.data == "main_menu")
async def handle_main_menu_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_inline_keyboard()
    )
    await callback.answer()

@router.message(F.text == "🏠 Menu")
async def handle_menu_button(message: types.Message):
    """Handle menu button click from the bottom panel."""
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_inline_keyboard()
    )

@router.message(lambda m: m.text == "New Request")
async def handle_new_request_menu(message: types.Message, state: FSMContext):
    """Handle New Request button from menu."""
    try:
        # Check if user has free requests remaining
        success = await user_service.add_free_request(message.from_user.id)
        if not success:
            await message.answer("You have no free requests remaining. Please purchase more requests or wait for your monthly quota to reset.")
            return

        # Ask for request description
        await message.answer("Please describe your request in detail. What kind of help or connection are you looking for?")
        await state.set_state(RequestStates.description)

    except Exception as e:
        logger.error(f"Error in New Request button handler: {e}")
        await message.answer("An error occurred. Please try again later.")

@router.callback_query(F.data == "new_request")
async def handle_new_request_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle New Request button from inline keyboard."""
    try:
        # Check if user has free requests remaining
        success = await user_service.add_free_request(callback.from_user.id)
        if not success:
            await callback.message.edit_text("You have no free requests remaining. Please purchase more requests or wait for your monthly quota to reset.")
            return

        # Ask for request description
        await callback.message.edit_text("Please describe your request in detail. What kind of help or connection are you looking for?")
        await state.set_state(RequestStates.description)

    except Exception as e:
        logger.error(f"Error in New Request callback handler: {e}")
        await callback.message.edit_text("An error occurred. Please try again later.") 