from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def edit_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with an edit profile button.
    
    Returns:
        InlineKeyboardMarkup: A keyboard containing a single button to edit profile.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Edit Profile",
                    callback_data="edit_profile"
                )
            ]
        ]
    )
    return keyboard

def skip_question_keyboard(question_identifier: str) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with a skip button for the current question.
    
    Args:
        question_identifier: Identifier for the current question (e.g., 'name', 'role')
        
    Returns:
        InlineKeyboardMarkup: A keyboard containing a single skip button.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️ Skip",
                    callback_data=f"skip_{question_identifier}"
                )
            ]
        ]
    )
    return keyboard 