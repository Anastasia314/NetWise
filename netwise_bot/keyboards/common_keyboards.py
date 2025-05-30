from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_initial_setup_keyboard() -> InlineKeyboardMarkup:
    """
    Create the initial setup keyboard.
    
    Returns:
        InlineKeyboardMarkup: The keyboard markup
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Create Profile", callback_data="create_profile")]
    ])
    return keyboard

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Create the main menu keyboard.
    
    Returns:
        InlineKeyboardMarkup: The keyboard markup
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Profile", callback_data="view_profile")],
        [InlineKeyboardButton(text="Edit Profile", callback_data="edit_profile")]
    ])
    return keyboard

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