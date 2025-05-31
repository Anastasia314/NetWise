"""
Keyboards for interaction-related buttons.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_helper_response_keyboard(request_id: str, requester_id: int) -> InlineKeyboardMarkup:
    """
    Get keyboard for helper's response to a help request.
    
    Args:
        request_id: The request ID
        requester_id: The Telegram ID of the requester
        
    Returns:
        InlineKeyboardMarkup with Yes/No buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Yes, I can help",
                    callback_data=f"accept_intro_{request_id}_{requester_id}"
                ),
                InlineKeyboardButton(
                    text="❌ No, I can't help",
                    callback_data=f"decline_intro_{request_id}_{requester_id}"
                )
            ]
        ]
    )

def get_introducer_response_keyboard(
    request_id: str,
    requester_id: int,
    helper_id: int
) -> InlineKeyboardMarkup:
    """
    Get keyboard for introducer's response to facilitate an introduction.
    
    Args:
        request_id: The request ID
        requester_id: The Telegram ID of the requester
        helper_id: The Telegram ID of the potential helper
        
    Returns:
        InlineKeyboardMarkup with Yes/No buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Yes, I'll facilitate",
                    callback_data=f"facilitate_intro_{request_id}_{requester_id}_{helper_id}"
                ),
                InlineKeyboardButton(
                    text="❌ No, I can't facilitate",
                    callback_data=f"decline_facilitate_{request_id}_{requester_id}_{helper_id}"
                )
            ]
        ]
    ) 