from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Creates the main menu reply keyboard with primary navigation options.
    
    Returns:
        ReplyKeyboardMarkup: A keyboard containing buttons for main menu options.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 My Profile"),
                KeyboardButton(text="➕ New Request")
            ],
            [
                KeyboardButton(text="🤝 My Friends"),
                KeyboardButton(text="🔗 Invite Friend")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard 