from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..services.user_service import UserService
from ..keyboards.profile_keyboards import get_profile_confirmation_keyboard, get_profile_cancel_keyboard, get_profile_edit_keyboard

# Create router for profile handlers
router = Router()

# Initialize UserService
user_service = UserService()

class ProfileStates(StatesGroup):
    name = State()
    role = State()
    industry = State()
    skills = State()
    goals = State()
    interests = State()

@router.callback_query(F.data == "create_profile")
async def process_create_profile(callback: types.CallbackQuery, state: FSMContext):
    """Handle the 'Create Profile' button click."""
    await callback.answer()
    await state.set_state(ProfileStates.name)
    await callback.message.answer(
        "Let's create your professional profile! What's your name or preferred display name?",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.name)
async def process_name(message: types.Message, state: FSMContext):
    """Process the name input and ask for role."""
    await state.update_data(name=message.text.strip())
    await state.set_state(ProfileStates.role)
    await message.answer(
        "Great! What's your current role or primary function? (e.g., Founder, Software Engineer, Product Manager)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.role)
async def process_role(message: types.Message, state: FSMContext):
    """Process the role input and ask for industry."""
    await state.update_data(role=message.text.strip())
    await state.set_state(ProfileStates.industry)
    await message.answer(
        "In which industry do you primarily work or are interested in? (e.g., Fintech, SaaS, HealthTech)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.industry)
async def process_industry(message: types.Message, state: FSMContext):
    """Process the industry input and ask for skills."""
    await state.update_data(industry=message.text.strip())
    await state.set_state(ProfileStates.skills)
    await message.answer(
        "What are some of your key skills? Please list them, separated by commas (e.g., Python, Project Management, UI/UX Design).",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.skills)
async def process_skills(message: types.Message, state: FSMContext):
    """Process the skills input and ask for goals."""
    skills = [s.strip() for s in message.text.split(',') if s.strip()]
    await state.update_data(skills=skills)
    await state.set_state(ProfileStates.goals)
    await message.answer(
        "What are your current professional goals or things you're looking to achieve? (comma-separated, e.g., Find co-founder, Get investment, Learn new tech).",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.goals)
async def process_goals(message: types.Message, state: FSMContext):
    """Process the goals input and ask for interests."""
    goals = [g.strip() for g in message.text.split(',') if g.strip()]
    await state.update_data(goals=goals)
    await state.set_state(ProfileStates.interests)
    await message.answer(
        "And finally, what are some of your professional interests? (comma-separated, e.g., AI, Blockchain, Remote Work).",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.interests)
async def process_interests(message: types.Message, state: FSMContext):
    """Process the interests input and show profile summary for confirmation."""
    interests = [i.strip() for i in message.text.split(',') if i.strip()]
    await state.update_data(interests=interests)
    
    # Get all collected data
    user_data = await state.get_data()
    
    # Format profile summary
    summary = (
        "📋 *Your Profile Summary*\n\n"
        f"👤 *Name:* {user_data['name']}\n"
        f"🏢 *Role:* {user_data['role']}\n"
        f"🏢 *Industry:* {user_data['industry']}\n"
        f"🛠 *Skills:* {', '.join(user_data['skills'])}\n"
        f"🎯 *Goals:* {', '.join(user_data['goals'])}\n"
        f"🌟 *Interests:* {', '.join(user_data['interests'])}\n\n"
        "Please review your profile. Would you like to confirm or edit it?"
    )
    
    await message.answer(
        summary,
        parse_mode="Markdown",
        reply_markup=get_profile_confirmation_keyboard()
    )

@router.callback_query(F.data == "confirm_profile")
async def process_profile_confirmation(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile confirmation and save to database."""
    await callback.answer()
    
    # Get all collected data
    user_data = await state.get_data()
    
    # Update profile in database
    success = user_service.update_profile(callback.from_user.id, user_data)
    
    if success:
        await callback.message.edit_text(
            "✅ Your profile has been successfully created! You can view it anytime using /myprofile",
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ Sorry, there was an error saving your profile. Please try again later.",
            parse_mode="Markdown"
        )
    
    # Clear the state
    await state.clear()

@router.callback_query(F.data == "edit_profile")
async def process_profile_edit(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile edit request."""
    await callback.answer()
    await state.set_state(ProfileStates.name)
    await callback.message.edit_text(
        "Let's update your profile! What's your name or preferred display name?",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.callback_query(F.data == "cancel_profile")
async def process_profile_cancellation(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile creation cancellation."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "Profile creation cancelled. You can create your profile later using /start",
        parse_mode="Markdown"
    )

def safe_join(val):
    if not val:
        return 'Not set'
    if isinstance(val, list):
        return ', '.join(val) if val else 'Not set'
    return str(val)

@router.message(Command("myprofile"))
async def show_profile(message: types.Message, telegram_id: int = None):
    """Show user's profile information."""
    user_id = telegram_id if telegram_id is not None else message.from_user.id
    profile = user_service.get_profile(user_id)
    
    if not profile:
        await message.answer(
            "You haven't created your profile yet. Use /start to create one!",
            parse_mode="Markdown"
        )
        return
    
    # Format profile information
    profile_text = (
        "\U0001F464 *Your Profile*\n\n"
        f"*Name:* {profile.get('name', 'Not set')}\n"
        f"*Role:* {profile.get('role', 'Not set')}\n"
        f"*Industry:* {profile.get('industry', 'Not set')}\n"
        f"*Skills:* {safe_join(profile.get('skills'))}\n"
        f"*Goals:* {safe_join(profile.get('goals'))}\n"
        f"*Interests:* {safe_join(profile.get('interests'))}\n"
        f"*Social Points:* {profile.get('social_points', 0)}\n"
        f"*Free Requests Remaining:* {profile.get('free_requests_remaining', 5)}\n"
    )
    
    await message.answer(
        profile_text,
        parse_mode="Markdown",
        reply_markup=get_profile_edit_keyboard()
    )

@router.message(Command("cancel"), StateFilter("*"))
async def cancel_any_state(message: types.Message, state: FSMContext):
    """Cancel any ongoing state."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("You are not in any active process.")
        return
    
    await state.clear()
    await message.answer(
        "Operation cancelled. You can start over using /start",
        parse_mode="Markdown"
    ) 