from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.db.queries import get_user_profile, set_user_inactive
from app.keyboards.inline import get_profile_management_keyboard, get_delete_confirmation_keyboard
from app.states.profile_creation import ProfileState
from app.services.supabase import get_supabase_client

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
        f"👤 <b>Ваш профиль:</b>\n\n"
        f"Имя: {profile['first_name']}\n"
        f"Компания: {profile['company']}\n"
        f"Должность: {profile['position']}\n"
        f"Индустрия: {profile['industries']['name']}\n"
        f"Теги: {', '.join(profile['tags'])}\n"
    )
    
    # Send profile with management keyboard
    await message.answer(
        profile_text,
        reply_markup=get_profile_management_keyboard()
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

@router.callback_query(F.data == "edit_profile")
async def edit_profile_callback(callback: CallbackQuery, state: FSMContext):
    """Handle edit profile button"""
    # Set editing mode
    await state.set_state(ProfileState.waiting_for_first_name)
    await state.update_data(editing_mode=True)
    
    await callback.message.edit_text(
        "✏️ Давайте обновим ваш профиль.\n"
        "Введите ваше имя:"
    ) 