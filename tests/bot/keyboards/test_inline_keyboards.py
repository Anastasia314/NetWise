import pytest
from aiogram.types import InlineKeyboardMarkup
from bot.keyboards.inline_keyboards import edit_profile_keyboard, skip_question_keyboard

def test_edit_profile_keyboard():
    """Test the edit profile keyboard creation."""
    keyboard = edit_profile_keyboard()
    
    # Check keyboard type
    assert isinstance(keyboard, InlineKeyboardMarkup)
    
    # Check button count
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1
    
    # Check button properties
    button = keyboard.inline_keyboard[0][0]
    assert button.text == "✏️ Edit Profile"
    assert button.callback_data == "edit_profile"

def test_skip_question_keyboard():
    """Test the skip question keyboard creation."""
    question_id = "name"
    keyboard = skip_question_keyboard(question_id)
    
    # Check keyboard type
    assert isinstance(keyboard, InlineKeyboardMarkup)
    
    # Check button count
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1
    
    # Check button properties
    button = keyboard.inline_keyboard[0][0]
    assert button.text == "➡️ Skip"
    assert button.callback_data == f"skip_{question_id}" 