from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """Create the main menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="My Profile")],
            [KeyboardButton(text="My Connections")],
            [KeyboardButton(text="New Request")],
            [KeyboardButton(text="Generate Invite")],
            [KeyboardButton(text="Toggle Search")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True
    )
    return keyboard

def get_profile_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 My Profile", callback_data="profile_view"),
                InlineKeyboardButton(text="👥 My Connections", callback_data="my_connections")
            ],
            [
                InlineKeyboardButton(text="📝 New Request", callback_data="new_request"),
                InlineKeyboardButton(text="🔗 Generate Invite", callback_data="generate_invite")
            ],
            [
                InlineKeyboardButton(text="🔄 Toggle Search", callback_data="toggle_search"),
                InlineKeyboardButton(text="❓ Help", callback_data="help")
            ]
        ]
    )

def get_main_menu_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 My Profile", callback_data="profile_view"),
                InlineKeyboardButton(text="👥 My Connections", callback_data="my_connections")
            ],
            [
                InlineKeyboardButton(text="📝 New Request", callback_data="new_request"),
                InlineKeyboardButton(text="🔗 Generate Invite", callback_data="generate_invite")
            ],
            [
                InlineKeyboardButton(text="🔄 Toggle Search", callback_data="toggle_search"),
                InlineKeyboardButton(text="❓ Help", callback_data="help")
            ]
        ]
    ) 