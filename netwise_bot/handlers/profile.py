from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..services.user_service import UserService
from ..keyboards.profile_keyboards import get_profile_confirmation_keyboard, get_profile_cancel_keyboard, get_profile_edit_keyboard, get_search_settings_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Create router for profile handlers
router = Router()

# Initialize UserService
user_service = UserService()

# Get logger
logger = logging.getLogger(__name__)

class ProfileStates(StatesGroup):
    """States for profile creation/editing."""
    waiting_for_name = State()
    waiting_for_role = State()
    waiting_for_industry = State()
    waiting_for_skills = State()
    waiting_for_goals = State()
    waiting_for_interests = State()

@router.callback_query(F.data == "create_profile")
async def process_create_profile(callback: types.CallbackQuery, state: FSMContext):
    """Handle the 'Create Profile' button click."""
    await callback.answer()
    await state.set_state(ProfileStates.waiting_for_name)
    await callback.message.answer(
        "Let's create your professional profile! What's your name or preferred display name?",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Process the name input and ask for role."""
    await state.update_data(name=message.text.strip())
    await state.set_state(ProfileStates.waiting_for_role)
    await message.answer(
        "Great! What's your current role or primary function? (e.g., Founder, Software Engineer, Product Manager)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_role)
async def process_role(message: types.Message, state: FSMContext):
    """Process the role input and ask for industry."""
    await state.update_data(role=message.text.strip())
    await state.set_state(ProfileStates.waiting_for_industry)
    await message.answer(
        "In which industry do you primarily work or are interested in? (e.g., Fintech, SaaS, HealthTech)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_industry)
async def process_industry(message: types.Message, state: FSMContext):
    """Process the industry input and ask for skills."""
    await state.update_data(industry=message.text.strip())
    await state.set_state(ProfileStates.waiting_for_skills)
    await message.answer(
        "What are some of your key skills? Please list them, separated by commas (e.g., Python, Project Management, UI/UX Design).",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_skills)
async def process_skills(message: types.Message, state: FSMContext):
    """Process the skills input and ask for goals."""
    skills = [s.strip() for s in message.text.split(',') if s.strip()]
    await state.update_data(skills=skills)
    await state.set_state(ProfileStates.waiting_for_goals)
    await message.answer(
        "What are your current professional goals or things you're looking to achieve? (comma-separated, e.g., Find co-founder, Get investment, Learn new tech).",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_goals)
async def process_goals(message: types.Message, state: FSMContext):
    """Process the goals input and ask for interests."""
    goals = [g.strip() for g in message.text.split(',') if g.strip()]
    await state.update_data(goals=goals)
    await state.set_state(ProfileStates.waiting_for_interests)
    await message.answer(
        "And finally, what are some of your professional interests? (comma-separated, e.g., AI, Blockchain, Remote Work).",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_interests)
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
    success = await user_service.update_profile(callback.from_user.id, user_data)
    
    if success:
        await callback.message.edit_text(
            "✅ Your profile has been successfully created!",
            parse_mode="Markdown"
        )
        await show_profile(callback.message, telegram_id=callback.from_user.id)
        
        # Prompt for search visibility
        await callback.message.answer(
            "Your profile is complete! Would you like to make yourself visible in search?",
            reply_markup=get_search_settings_keyboard()
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
    await state.set_state(ProfileStates.waiting_for_name)
    await callback.message.edit_text(
        "✏️ *Profile Editor*\n\n"
        "Let's update your profile. Please enter your name:",
        parse_mode="Markdown",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.callback_query(F.data == "cancel_profile")
async def process_profile_cancellation(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile creation cancellation."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "Profile creation cancelled. You can create your profile later using menu",
        parse_mode="Markdown"
    )

def safe_join(items: list) -> str:
    """Safely join list items, handling None values."""
    if not items:
        return "Not set"
    return ", ".join(str(item) for item in items if item is not None)

@router.message(Command("myprofile"))
async def show_profile(message: types.Message, telegram_id: int) -> None:
    """Show user profile."""
    try:
        # Get user profile
        profile = await user_service.get_profile(telegram_id)
        
        if not profile:
            await message.answer("❌ Profile not found.")
            return
            
        # Format profile data
        profile_text = (
            f"*Name:* {profile.get('name', 'Not set')}\n"
            f"*Role:* {profile.get('role', 'Not set')}\n"
            f"*Industry:* {profile.get('industry', 'Not set')}\n"
            f"*Skills:* {safe_join(profile.get('skills', []))}\n"
            f"*Goals:* {safe_join(profile.get('goals', []))}\n"
            f"*Interests:* {safe_join(profile.get('interests', []))}\n"
            f"*Social Points:* {profile.get('social_points', 0)}\n"
            f"*Free Requests Remaining:* {profile.get('free_requests_remaining', 0)}\n"
            f"*Active in Search:* {'Yes' if profile.get('is_active_in_search') else 'No'}\n"
            f"*Last Active:* {profile.get('last_active_at', 'Never')}"
        )
        
        # Create inline keyboard for profile actions
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit Profile", callback_data="edit_profile"),
                InlineKeyboardButton(text="🔄 Toggle Search", callback_data="toggle_search")
            ],
            [
                InlineKeyboardButton(text="🔗 Generate Invite", callback_data="generate_invite"),
                InlineKeyboardButton(text="👥 My Connections", callback_data="my_connections")
            ]
        ])
        
        await message.answer(
            f"*Your Profile:*\n\n{profile_text}",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing profile: {e}")
        await message.answer("❌ An error occurred while fetching your profile.")

@router.message(Command("cancel"), StateFilter("*"))
async def cancel_profile_edit(message: types.Message, state: FSMContext):
    """Cancel profile editing."""
    current_state = await state.get_state()
    if current_state is None:
        return
        
    await state.clear()
    await message.answer(
        "❌ Profile editing cancelled.",
        reply_markup=get_profile_edit_keyboard()
    )

@router.message(ProfileStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Process user's name input."""
    await state.update_data(name=message.text)
    await state.set_state(ProfileStates.waiting_for_role)
    await message.answer(
        "Great! Now, what's your role or position?",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_role)
async def process_role(message: types.Message, state: FSMContext):
    """Process user's role input."""
    await state.update_data(role=message.text)
    await state.set_state(ProfileStates.waiting_for_industry)
    await message.answer(
        "What industry are you in?",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_industry)
async def process_industry(message: types.Message, state: FSMContext):
    """Process user's industry input."""
    await state.update_data(industry=message.text)
    await state.set_state(ProfileStates.waiting_for_skills)
    await message.answer(
        "What are your key skills? (comma-separated)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_skills)
async def process_skills(message: types.Message, state: FSMContext):
    """Process user's skills input."""
    skills = [skill.strip() for skill in message.text.split(",")]
    await state.update_data(skills=skills)
    await state.set_state(ProfileStates.waiting_for_goals)
    await message.answer(
        "What are your professional goals? (comma-separated)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_goals)
async def process_goals(message: types.Message, state: FSMContext):
    """Process user's goals input."""
    goals = [goal.strip() for goal in message.text.split(",")]
    await state.update_data(goals=goals)
    await state.set_state(ProfileStates.waiting_for_interests)
    await message.answer(
        "What are your professional interests? (comma-separated)",
        reply_markup=get_profile_cancel_keyboard()
    )

@router.message(ProfileStates.waiting_for_interests)
async def process_interests(message: types.Message, state: FSMContext):
    """Process user's interests input and save profile."""
    try:
        interests = [interest.strip() for interest in message.text.split(",")]
        data = await state.get_data()
        data['interests'] = interests
        
        # Update profile
        success = await user_service.update_profile(message.from_user.id, data)
        
        if success:
            await message.answer(
                "✅ Profile updated successfully!",
                reply_markup=get_profile_edit_keyboard()
            )
        else:
            await message.answer(
                "❌ Failed to update profile. Please try again.",
                reply_markup=get_profile_edit_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        await message.answer(
            "❌ An error occurred while updating your profile.",
            reply_markup=get_profile_edit_keyboard()
        )
        
    finally:
        await state.clear()

@router.callback_query(lambda c: c.data == "toggle_search")
async def toggle_search_status(callback: types.CallbackQuery):
    """Toggle user's visibility in search."""
    try:
        # Get current user
        user = await user_service.get_or_create_user(callback.from_user.id)
        if not user:
            await callback.answer("❌ Error: User not found", show_alert=True)
            return
            
        # Toggle search status
        new_status = not user.get('is_active_in_search', True)
        success = await user_service.set_search_status(callback.from_user.id, new_status)
        
        if success:
            status_text = "visible" if new_status else "hidden"
            await callback.message.answer(
                f"✅ Your profile is now {status_text} in search results."
            )
        else:
            await callback.message.answer("❌ Failed to update search status.")
            
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error toggling search status: {e}")
        await callback.answer("❌ Error updating search status", show_alert=True) 