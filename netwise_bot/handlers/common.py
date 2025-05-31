from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..services.user_service import UserService
from ..services.graph_service import GraphService
from ..keyboards.common_keyboards import get_initial_setup_keyboard, get_main_menu_keyboard, get_search_settings_keyboard
from ..states.profile_states import ProfileStates
from ..handlers.profile import show_profile

# Create router for common handlers
router = Router()

# Initialize UserService
user_service = UserService()

@router.message(Command("start"))
async def handle_start(
    message: types.Message,
    state: FSMContext,
    user_service: UserService = None,
    graph_service: GraphService = None
):
    """Handle /start command and invite links."""
    # Check if this is an invite link
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("invite_"):
        try:
            # Extract inviter's Telegram ID
            inviter_telegram_id = int(args[1].split("_")[1])
            
            # Prevent self-invites
            if inviter_telegram_id == message.from_user.id:
                await message.answer(
                    "Welcome to NetWise! You can't invite yourself. "
                    "Let's get started with your profile setup."
                )
            else:
                # Get or create the new user
                user = await user_service.get_or_create_user(
                    message.from_user.id,
                    message.from_user.full_name
                )
                
                if not user:
                    await message.answer(
                        "Welcome to NetWise! There was an error creating your account. "
                        "Please try again later."
                    )
                    return
                    
                # Check if connection already exists
                existing_connection = await graph_service.get_connection(
                    str(inviter_telegram_id),
                    str(message.from_user.id)
                )
                
                if existing_connection:
                    await message.answer(
                        "Welcome to NetWise! You're already connected with this user. "
                        "Let's continue with your profile setup."
                    )
                else:
                    # Process the invite
                    if await graph_service.process_invite(inviter_telegram_id, message.from_user.id):
                        # Get inviter's name for the message
                        inviter = await user_service.get_profile(inviter_telegram_id)
                        inviter_name = inviter.get('name', 'A user') if inviter else 'A user'
                        
                        await message.answer(
                            f"Welcome to NetWise! You've been invited by {inviter_name}. "
                            "You're now connected in the network!"
                        )
                        
                        # Notify the inviter
                        try:
                            await message.bot.send_message(
                                inviter_telegram_id,
                                f"Great news! {message.from_user.full_name} has joined NetWise through your invite link!"
                            )
                        except Exception as e:
                            print(f"Could not notify inviter: {e}")
                    else:
                        await message.answer(
                            "Welcome to NetWise! There was an error processing your invite. "
                            "You can still use the bot normally."
                        )
        except (ValueError, IndexError):
            # If there's any error parsing the invite, just proceed with normal start
            await message.answer(
                "Welcome to NetWise! The invite link appears to be invalid. "
                "Let's get started with your profile setup."
            )
    
    # Get or create user
    user = await user_service.get_or_create_user(
        message.from_user.id,
        message.from_user.full_name
    )
    
    if not user:
        await message.answer(
            "Welcome to NetWise! There was an error creating your account. "
            "Please try again later."
        )
        return
    
    # Check if user has a profile
    profile = await user_service.get_profile(message.from_user.id)
    
    if not profile:
        # New user without profile
        await message.answer(
            "Welcome to NetWise! Let's create your professional profile to help you "
            "connect with the right people.",
            reply_markup=get_initial_setup_keyboard()
        )
    else:
        # Existing user with profile
        await message.answer(
            f"Welcome back to NetWise, {profile.get('name', 'there')}! "
            "What would you like to do?",
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