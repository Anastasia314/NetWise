"""
Keyboards for request-related interactions.
"""
from typing import List, Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_request_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for confirming request submission.
    
    Returns:
        InlineKeyboardMarkup with Submit and Cancel buttons
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Submit Request",
                    callback_data="submit_request"
                ),
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data="cancel_request"
                )
            ]
        ]
    )

def get_request_cancellation_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for cancelling request creation.
    
    Returns:
        InlineKeyboardMarkup with Cancel button
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Cancel Request",
                    callback_data="cancel_request"
                )
            ]
        ]
    )

def get_ask_help_keyboard(
    request_id: str,
    potential_helpers: List[Dict]
) -> InlineKeyboardMarkup:
    """
    Get keyboard for asking potential helpers for help.
    
    Args:
        request_id: The request ID
        potential_helpers: List of potential helpers with their details
        
    Returns:
        InlineKeyboardMarkup with Ask for Help buttons
    """
    buttons = []
    
    for helper in potential_helpers:
        buttons.append([
            InlineKeyboardButton(
                text=f"Ask {helper['name']} for help",
                callback_data=f"ask_help_{request_id}_{helper['user_id']}"
            )
        ])
    
    # Add a "Cancel" button at the bottom
    buttons.append([
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data="cancel_request"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons) 