from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_delete_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for profile deletion confirmation"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data="confirm_delete"
        ),
        InlineKeyboardButton(
            text="❌ Нет, отмена",
            callback_data="cancel_delete"
        )
    )
    
    return builder.as_markup() 