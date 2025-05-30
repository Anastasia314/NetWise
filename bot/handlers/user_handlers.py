from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from bot.services.api_client import APIClient, APIClientError
from bot.states.user_states import ProfileSetup
from bot.keyboards.inline_keyboards import edit_profile_keyboard
from bot.keyboards.reply_keyboards import main_menu_keyboard
from bot.utils.formatters import format_user_profile_message

# Create router instance
user_router = Router()

@user_router.message(CommandStart())
async def handle_start(
    message: types.Message,
    state: FSMContext,
    api_client: APIClient
) -> None:
    """
    Handle the /start command.
    Onboards new users and either initiates profile setup or shows main menu.
    """
    user = message.from_user
    telegram_id = user.id
    name = user.first_name
    username = user.username

    try:
        # Attempt to onboard user
        await api_client.onboard_user(telegram_id, name, username)
        
        # Get user profile
        profile = await api_client.get_user_profile(telegram_id)
        
        # Check if profile is complete
        is_complete = all([
            profile.get("role"),
            profile.get("industry"),
            profile.get("skills")
        ])
        
        if not is_complete:
            # New user or incomplete profile
            await message.answer(
                "👋 Welcome to NetWise! Let's set up your profile to help you connect with the right people."
            )
            await state.set_state(ProfileSetup.ASK_NAME)
            await message.answer("What is your preferred display name?")
        else:
            # Existing user with complete profile
            await message.answer(
                f"👋 Welcome back, {name}! Here's your main menu:",
                reply_markup=main_menu_keyboard()
            )
            await state.clear()
            
    except APIClientError as e:
        await message.answer(
            "😔 Sorry, we're having trouble connecting to our services. Please try again later."
        )

@user_router.message(Command("profile"))
async def handle_profile(
    message: types.Message,
    api_client: APIClient
) -> None:
    """
    Handle the /profile command.
    Displays the user's current profile information.
    """
    telegram_id = message.from_user.id
    
    try:
        profile = await api_client.get_user_profile(telegram_id)
        formatted_profile = format_user_profile_message(profile)
        
        await message.answer(
            formatted_profile,
            reply_markup=edit_profile_keyboard(),
            parse_mode="MarkdownV2"
        )
        
    except APIClientError as e:
        await message.answer(
            "😔 Sorry, we couldn't fetch your profile. Please try again later."
        ) 