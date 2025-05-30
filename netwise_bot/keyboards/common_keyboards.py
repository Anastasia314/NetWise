from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_initial_setup_keyboard() -> InlineKeyboardMarkup:
    """
    Create the initial setup keyboard.
    
    Returns:
        InlineKeyboardMarkup: The keyboard markup
    """
    keyboard = [
        [InlineKeyboardButton(text="Create Profile", callback_data="create_profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create the main menu keyboard.
    
    Returns:
        ReplyKeyboardMarkup: The keyboard markup
    """
    keyboard = [
        [KeyboardButton(text="👤 Create Profile"), KeyboardButton(text="🔍 Search Settings")],
        [KeyboardButton(text="🔗 Find Connections"), KeyboardButton(text="📋 My Profile")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_search_settings_keyboard() -> InlineKeyboardMarkup:
    """
    Create the search settings keyboard.
    
    Returns:
        InlineKeyboardMarkup: The keyboard markup
    """
    keyboard = [
        [
            InlineKeyboardButton(text="👁️ Show in Search", callback_data="search_show"),
            InlineKeyboardButton(text="🙈 Hide from Search", callback_data="search_hide")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 