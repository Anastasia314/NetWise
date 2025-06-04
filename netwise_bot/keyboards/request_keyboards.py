"""
Keyboards for request-related interactions.
"""
from typing import List, Dict, Any, Optional
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

def get_request_list_keyboard(
    requests: List[Dict[str, Any]],
    page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    """Create keyboard for request list view."""
    keyboard_buttons = []
    
    # Add request buttons
    for req in requests:
        # Format request preview (first 30 chars of description)
        preview = req["description_text"][:30] + "..." if len(req["description_text"]) > 30 else req["description_text"]
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📝 {preview}",
                callback_data=f"request_details_{req['id']}"
            )
        ])
    
    # Add pagination buttons
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"request_page_{page-1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"request_page_{page+1}"
            )
        )
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_request_details_keyboard(request_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for request details view."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"request_edit_{request_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"request_delete_{request_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад к списку",
                    callback_data="back_to_list"
                )
            ]
        ]
    )
    return keyboard

def get_request_edit_keyboard(request_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for request editing."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💾 Сохранить",
                    callback_data=f"request_save_{request_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"request_details_{request_id}"
                )
            ]
        ]
    )
    return keyboard

def get_request_delete_confirm_keyboard(request_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for request deletion confirmation."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"confirm_delete_{request_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="back_to_list"
                )
            ]
        ]
    )
    return keyboard

def get_request_stats_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for request statistics view."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="⬅️ Back to List",
                callback_data="req_back_to_list"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 