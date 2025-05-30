import pytest
from aiogram.types import ReplyKeyboardMarkup
from bot.keyboards.reply_keyboards import main_menu_keyboard

def test_main_menu_keyboard():
    """Test the main menu keyboard creation."""
    keyboard = main_menu_keyboard()
    
    # Check keyboard type
    assert isinstance(keyboard, ReplyKeyboardMarkup)
    
    # Check keyboard properties
    assert keyboard.resize_keyboard is True
    assert keyboard.one_time_keyboard is False
    
    # Check button layout
    assert len(keyboard.keyboard) == 2  # Two rows
    assert len(keyboard.keyboard[0]) == 2  # Two buttons in first row
    assert len(keyboard.keyboard[1]) == 2  # Two buttons in second row
    
    # Check button texts
    assert keyboard.keyboard[0][0].text == "👤 My Profile"
    assert keyboard.keyboard[0][1].text == "➕ New Request"
    assert keyboard.keyboard[1][0].text == "🤝 My Friends"
    assert keyboard.keyboard[1][1].text == "🔗 Invite Friend" 