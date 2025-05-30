from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_profile_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for confirming profile submission.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with "Confirm" and "Edit" buttons
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data="confirm_profile"),
                InlineKeyboardButton(text="✏️ Edit", callback_data="edit_profile")
            ],
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_profile")
            ]
        ]
    )
    return keyboard

def get_profile_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for canceling profile creation.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with "Cancel" button
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_profile")
            ]
        ]
    )
    return keyboard

def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for editing profile."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit Profile", callback_data="edit_profile")
            ]
        ]
    )
    return keyboard 