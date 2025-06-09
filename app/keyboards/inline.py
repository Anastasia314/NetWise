from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

logger = logging.getLogger(__name__)

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

def get_contact_card_keyboard(user_telegram_id: int) -> InlineKeyboardMarkup:
    """Get keyboard with a button to contact user via Telegram
    
    Args:
        user_telegram_id: Telegram ID of the user to contact
        
    Returns:
        InlineKeyboardMarkup with contact button
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💬 Написать",
            url=f"tg://user?id={user_telegram_id}"
        )
    )
    
    return builder.as_markup()

def get_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Create pagination keyboard with navigation buttons.
    
    Args:
        current_page: Current page number
        total_pages: Total number of pages
        
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    logger.info("="*50)
    logger.info("CREATING PAGINATION KEYBOARD")
    logger.info(f"Current page: {current_page}, Total pages: {total_pages}")
    
    keyboard = []
    row = []
    
    # Add left arrow if not on first page
    if current_page > 1:
        prev_page = current_page - 1
        callback_data = f"pagination:{prev_page}"
        logger.info(f"Adding prev button with callback_data: {callback_data}")
        row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=callback_data
        ))
    
    # Add current page indicator
    row.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="ignore"  # This button is just for display
    ))
    
    # Add right arrow if not on last page
    if current_page < total_pages:
        next_page = current_page + 1
        callback_data = f"pagination:{next_page}"
        logger.info(f"Adding next button with callback_data: {callback_data}")
        row.append(InlineKeyboardButton(
            text="➡️",
            callback_data=callback_data
        ))
    
    keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard) 