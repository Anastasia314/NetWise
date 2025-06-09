from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

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

@router.callback_query(F.data.in_([
    "edit_first_name",
    "edit_last_name",
    "edit_company",
    "edit_title",
    "edit_industry",
    "edit_tags"
]))
async def edit_field_callback(callback: CallbackQuery, state: FSMContext):
    """Handle edit field button"""
    # Load current profile data into state
    profile = get_user_profile(get_supabase_client(), callback.from_user.id)
    if profile:
        # Get tag IDs
        tag_ids = []
        if profile['tags']:
            result = get_supabase_client().table("tags") \
                .select("id") \
                .in_("name", profile['tags']) \
                .execute()
            tag_ids = [tag["id"] for tag in result.data]
        
        # Update state with profile data
        await state.update_data(
            first_name=profile['first_name'],
            last_name=profile['last_name'],
            company=profile['company'],
            title=profile['title'],
            industry_id=profile['industry_id'],
            industry=profile['industries']['name'],
            own_tags=tag_ids,
            editing_mode=True
        )

    # Use the edit field handler from profile_creation
    await process_edit_field(callback, state)