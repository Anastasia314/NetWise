"""
Keyboards for request-related interactions.
"""
from typing import List, Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

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

def get_ask_help_keyboard(request_id: str, potential_helpers: List[Dict]) -> InlineKeyboardMarkup:
    """
    Create keyboard for asking potential helpers for help.
    
    Args:
        request_id: ID of the request
        potential_helpers: List of potential helpers with their match scores
        
    Returns:
        InlineKeyboardMarkup with buttons for each potential helper
    """
    keyboard = []
    logger = logging.getLogger(__name__)
    
    logger.info(f"Creating ask_help keyboard for request_id={request_id}")
    logger.info(f"Number of potential helpers: {len(potential_helpers)}")
    
    for helper in potential_helpers:
        match_score = helper.get('match_score', 0)
        button_text = f"Ask {helper['name']} ({match_score}% match)"
        callback_data = f"ah_{helper['user_id']}_{match_score}"  # Include match_score in callback data
        logger.info(f"Creating button: text='{button_text}', callback_data='{callback_data}', user_id='{helper['user_id']}'")
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Cancel",
            callback_data="cancel_request"
        )
    ])
    
    logger.info("Keyboard created successfully")
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 