from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.queries import get_user_profile, set_user_inactive
from app.keyboards.inline import get_delete_confirmation_keyboard
from app.states.profile_states import ProfileState
from app.db.session import get_supabase_client
from app.handlers.profile_creation import (
    process_first_name,
    process_last_name,
    process_company,
    process_title,
    process_industry,
    process_tags,
    get_industry_keyboard,
    get_tags_keyboard,
    get_edit_profile_keyboard,
    get_profile_preview_keyboard,
    process_edit_field
)

router = Router()

@router.message(Command("myprofile"))
async def cmd_myprofile(message: Message):
    """Handle /myprofile command"""
    # Get user profile
    profile = get_user_profile(get_supabase_client(), message.from_user.id)
    
    if not profile:
        await message.answer(
            "❌ У вас еще нет профиля. Используйте /start для создания."
        )
        return
    
    # Format profile message
    profile_text = (
        "📝 Проверь свой профиль:\n\n"
        f"👤 Имя: {profile['first_name']} {profile['last_name']}\n"
        f"🏢 Компания: {profile['company']}\n"
        f"💼 Должность: {profile['title']}\n"
        f"🏭 Индустрия: {profile['industries']['name']}\n"
        f"🏷️ Теги: {', '.join(profile['tags'])}\n\n"
        "Все правильно или нужно обновить?"
    )
    
    # Send profile with edit keyboard
    await message.answer(
        profile_text,
        reply_markup=get_edit_profile_keyboard()
    )

@router.callback_query(F.data == "delete_profile")
async def delete_profile_callback(callback: CallbackQuery):
    """Handle delete profile button"""
    await callback.message.edit_text(
        "⚠️ Вы уверены, что хотите удалить свой профиль?\n"
        "Это действие нельзя будет отменить.",
        reply_markup=get_delete_confirmation_keyboard()
    )

@router.callback_query(F.data == "confirm_delete")
async def confirm_delete_callback(callback: CallbackQuery):
    """Handle profile deletion confirmation"""
    if set_user_inactive(get_supabase_client(), callback.from_user.id):
        await callback.message.edit_text(
            "✅ Ваш профиль успешно удален.\n"
            "Вы можете создать новый профиль с помощью команды /start"
        )
    else:
        await callback.message.edit_text(
            "❌ Произошла ошибка при удалении профиля.\n"
            "Пожалуйста, попробуйте позже."
        )

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_callback(callback: CallbackQuery):
    """Handle deletion cancellation"""
    await callback.message.edit_text(
        "❌ Удаление профиля отменено."
    )

@router.callback_query(F.data.startswith("edit_"))
async def handle_edit_field(callback: CallbackQuery, state: FSMContext):
    """Handle edit field selection"""
    # Get current user
    user_result = get_supabase_client().table("users") \
        .select("*, industries!inner(*), user_tags(tags(id, name))") \
        .eq("telegram_id", callback.from_user.id) \
        .single() \
        .execute()
    
    if not user_result.data:
        await callback.answer("❌ Сначала создайте свой профиль!")
        return
    
    # Load current profile data into state
    await state.update_data(
        first_name=user_result.data.get("first_name", ""),
        last_name=user_result.data.get("last_name", ""),
        company=user_result.data.get("company", ""),
        title=user_result.data.get("title", ""),
        industry_id=user_result.data.get("industry_id"),
        industry=user_result.data.get("industries", {}).get("name", ""),
        own_tags=[tag["tags"]["id"] for tag in user_result.data.get("user_tags", [])],
        editing_mode=True
    )
    
    # Use the process_edit_field function from profile_creation
    await process_edit_field(callback, state)

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery, state: FSMContext):
    """Return to profile view"""
    # Get current user
    user_result = get_supabase_client().table("users") \
        .select("*, industries!inner(*), user_tags(tags(name))") \
        .eq("telegram_id", callback.from_user.id) \
        .single() \
        .execute()
    
    if not user_result.data:
        await callback.answer("❌ Сначала создайте свой профиль!")
        return
    
    # Format profile
    profile_text = (
        "📝 Проверь свой профиль:\n\n"
        f"👤 Имя: {user_result.data['first_name']} {user_result.data['last_name']}\n"
        f"🏢 Компания: {user_result.data['company']}\n"
        f"💼 Должность: {user_result.data['title']}\n"
        f"🏭 Индустрия: {user_result.data['industries']['name']}\n"
        f"🏷️ Теги: {', '.join([tag['tags']['name'] for tag in user_result.data['user_tags']])}\n\n"
        "Все правильно или нужно обновить?"
    )
    
    # Create keyboard
    keyboard = get_edit_profile_keyboard()
    
    # Show profile
    await callback.message.edit_text(
        profile_text,
        reply_markup=keyboard
    )
    
    # Reset state
    await state.clear()
    
    await callback.answer()

# Reuse handlers from profile_creation
@router.message(ProfileState.waiting_for_first_name)
async def handle_first_name(message: Message, state: FSMContext):
    await process_first_name(message, state)

@router.message(ProfileState.waiting_for_last_name)
async def handle_last_name(message: Message, state: FSMContext):
    await process_last_name(message, state)

@router.message(ProfileState.waiting_for_company)
async def handle_company(message: Message, state: FSMContext):
    await process_company(message, state)

@router.message(ProfileState.waiting_for_title)
async def handle_title(message: Message, state: FSMContext):
    await process_title(message, state)

@router.callback_query(ProfileState.waiting_for_industry, F.data.startswith("industry:"))
async def handle_industry(callback: CallbackQuery, state: FSMContext):
    await process_industry(callback, state)

@router.callback_query(ProfileState.waiting_for_own_tags, F.data.startswith("tag:"))
async def handle_tag_selection(callback: CallbackQuery, state: FSMContext):
    await process_tags(callback, state)