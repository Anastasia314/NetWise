from aiogram import Router, types
from aiogram.filters import Command, CommandStart, StateFilter
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

@user_router.message(ProfileSetup.ASK_NAME)
async def process_ask_name(message: types.Message, state: FSMContext) -> None:
    """Process user's name input and ask for role."""
    name = message.text.strip()
    await state.update_data(name=name)
    
    await message.answer(
        f"Great, {name}! Now, what's your current role or primary function? "
        "(e.g., Founder, Software Engineer, Product Manager)"
    )
    await state.set_state(ProfileSetup.ASK_ROLE)

@user_router.message(ProfileSetup.ASK_ROLE)
async def process_ask_role(message: types.Message, state: FSMContext) -> None:
    """Process user's role input and ask for industry."""
    role = message.text.strip()
    await state.update_data(role=role)
    
    await message.answer(
        "Got it. In which industry do you primarily work or are interested in? "
        "(e.g., Fintech, SaaS, HealthTech)"
    )
    await state.set_state(ProfileSetup.ASK_INDUSTRY)

@user_router.message(ProfileSetup.ASK_INDUSTRY)
async def process_ask_industry(message: types.Message, state: FSMContext) -> None:
    """Process user's industry input and ask for skills."""
    industry = message.text.strip()
    await state.update_data(industry=industry)
    
    await message.answer(
        "What are some of your key skills? Please list them, separated by commas "
        "(e.g., Python, Project Management, UI/UX Design)."
    )
    await state.set_state(ProfileSetup.ASK_SKILLS)

@user_router.message(ProfileSetup.ASK_SKILLS)
async def process_ask_skills(message: types.Message, state: FSMContext) -> None:
    """Process user's skills input and ask for goals."""
    skills = [s.strip() for s in message.text.split(',') if s.strip()]
    await state.update_data(skills=skills)
    
    await message.answer(
        "What are your current professional goals or things you're looking to achieve? "
        "(comma-separated, e.g., Find co-founder, Get investment, Learn new tech)."
    )
    await state.set_state(ProfileSetup.ASK_GOALS)

@user_router.message(ProfileSetup.ASK_GOALS)
async def process_ask_goals(message: types.Message, state: FSMContext) -> None:
    """Process user's goals input and ask for interests."""
    goals = [g.strip() for g in message.text.split(',') if g.strip()]
    await state.update_data(goals=goals)
    
    await message.answer(
        "And finally, what are some of your professional interests? "
        "(comma-separated, e.g., AI, Blockchain, Remote Work)."
    )
    await state.set_state(ProfileSetup.ASK_INTERESTS)

@user_router.message(ProfileSetup.ASK_INTERESTS)
async def process_ask_interests(
    message: types.Message,
    state: FSMContext,
    api_client: APIClient
) -> None:
    """Process user's interests input and submit profile to API."""
    interests = [i.strip() for i in message.text.split(',') if i.strip()]
    await state.update_data(interests=interests)
    
    # Get all collected data
    user_data = await state.get_data()
    
    try:
        # Submit profile to API
        await api_client.update_user_profile(
            telegram_id=message.from_user.id,
            profile_data=user_data
        )
        
        # Success message and main menu
        await message.answer(
            "✅ Your profile has been updated successfully!",
            reply_markup=main_menu_keyboard()
        )
        
    except APIClientError as e:
        await message.answer(
            "😔 Sorry, there was an issue updating your profile. Please try again later."
        )
    
    # Clear state regardless of success/failure
    await state.clear()

@user_router.callback_query(lambda c: c.data == "edit_profile")
async def handle_edit_profile_callback(
    callback_query: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Handle the 'Edit Profile' button click."""
    await callback_query.answer()
    
    await callback_query.message.answer(
        "Let's update your profile. What is your name/preferred display name? "
        "If unchanged, just send your current one."
    )
    await state.set_state(ProfileSetup.ASK_NAME)

@user_router.message(Command("cancel"), StateFilter("*"))
async def handle_cancel_fsm(message: types.Message, state: FSMContext) -> None:
    """Handle the /cancel command to exit FSM."""
    current_state = await state.get_state()
    
    if current_state is not None:
        await message.answer(
            "Profile setup cancelled.",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()
    else:
        await message.answer("You are not in any active process.") 