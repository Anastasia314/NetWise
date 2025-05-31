"""
Handlers for interaction-related commands and callbacks.
"""
import logging
from typing import Optional, Tuple
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from netwise_bot.services.supabase_client import supabase_client
from netwise_bot.services.user_service import user_service
from netwise_bot.services.request_service import request_service
from netwise_bot.keyboards.interaction_keyboards import (
    get_helper_response_keyboard,
    get_introducer_response_keyboard
)

# Initialize router
router = Router()

# Initialize logger
logger = logging.getLogger(__name__)

class InteractionStates(StatesGroup):
    """States for interaction flow."""
    waiting_for_helper_response = State()
    waiting_for_introducer_response = State()

async def handle_ask_for_help(
    callback: CallbackQuery,
    state: FSMContext,
    request_id: str,
    helper_id: int
) -> None:
    """
    Handle the initial "Ask for help" button click.
    
    Args:
        callback: The callback query
        state: The FSM context
        request_id: The request ID
        helper_id: The Telegram ID of the potential helper
    """
    try:
        # Get request details
        request = request_service.get_request(request_id)
        if not request:
            await callback.answer("Request not found")
            return

        # Get connection type between users
        connection_type = user_service.get_connection_type(
            request["requester_id"],
            helper_id
        )

        if connection_type == "direct":
            # Direct connection - ask helper directly
            await handle_direct_connection(callback, request, helper_id)
        elif connection_type == "indirect":
            # Indirect connection - need introducer
            await handle_indirect_connection(callback, state, request, helper_id)
        else:
            await callback.answer("No connection found between users")

    except Exception as e:
        logger.error(f"Error handling ask for help: {e}")
        await callback.answer("An error occurred")

async def handle_direct_connection(
    callback: CallbackQuery,
    request: dict,
    helper_id: int
) -> None:
    """
    Handle direct connection between users.
    
    Args:
        callback: The callback query
        request: The request details
        helper_id: The Telegram ID of the helper
    """
    try:
        # Log the match
        await log_request_match(request["id"], helper_id)

        # Send message to helper
        helper_message = (
            f"🔔 New help request!\n\n"
            f"From: {request['requester_name']}\n"
            f"Request: {request['description']}\n\n"
            f"Can you help with this request?"
        )
        
        keyboard = get_helper_response_keyboard(request["id"], request["requester_id"])
        await callback.bot.send_message(
            chat_id=helper_id,
            text=helper_message,
            reply_markup=keyboard
        )

        await callback.answer("Request sent to helper")

    except Exception as e:
        logger.error(f"Error handling direct connection: {e}")
        await callback.answer("An error occurred")

async def handle_indirect_connection(
    callback: CallbackQuery,
    state: FSMContext,
    request: dict,
    helper_id: int
) -> None:
    """
    Handle indirect connection between users.
    
    Args:
        callback: The callback query
        state: The FSM context
        request: The request details
        helper_id: The Telegram ID of the helper
    """
    try:
        # Get introducer
        introducer = user_service.get_common_connection(
            request["requester_id"],
            helper_id
        )
        
        if not introducer:
            await callback.answer("No common connection found")
            return

        # Log the match
        await log_request_match(
            request["id"],
            helper_id,
            introducer_id=introducer["id"]
        )

        # Send message to introducer
        introducer_message = (
            f"🔔 Introduction request!\n\n"
            f"From: {request['requester_name']}\n"
            f"To: {helper_id}\n"
            f"Request: {request['description']}\n\n"
            f"Would you like to facilitate this introduction?"
        )
        
        keyboard = get_introducer_response_keyboard(
            request["id"],
            request["requester_id"],
            helper_id
        )
        
        await callback.bot.send_message(
            chat_id=introducer["id"],
            text=introducer_message,
            reply_markup=keyboard
        )

        await callback.answer("Request sent to introducer")

    except Exception as e:
        logger.error(f"Error handling indirect connection: {e}")
        await callback.answer("An error occurred")

async def handle_helper_response(
    callback: CallbackQuery,
    request_id: str,
    requester_id: int,
    accepted: bool
) -> None:
    """
    Handle helper's response to a help request.
    
    Args:
        callback: The callback query
        request_id: The request ID
        requester_id: The Telegram ID of the requester
        accepted: Whether the helper accepted the request
    """
    try:
        # Update match status
        await update_match_status(
            request_id,
            callback.from_user.id,
            "accepted" if accepted else "declined"
        )

        # Notify requester
        status = "accepted" if accepted else "declined"
        requester_message = (
            f"Your help request has been {status} by {callback.from_user.full_name}"
        )
        await callback.bot.send_message(
            chat_id=requester_id,
            text=requester_message
        )

        await callback.answer("Response sent")

    except Exception as e:
        logger.error(f"Error handling helper response: {e}")
        await callback.answer("An error occurred")

async def handle_introducer_response(
    callback: CallbackQuery,
    request_id: str,
    requester_id: int,
    helper_id: int,
    accepted: bool
) -> None:
    """
    Handle introducer's response to facilitate an introduction.
    
    Args:
        callback: The callback query
        request_id: The request ID
        requester_id: The Telegram ID of the requester
        helper_id: The Telegram ID of the helper
        accepted: Whether the introducer accepted the request
    """
    try:
        if accepted:
            # Send message to helper
            helper_message = (
                f"🔔 New help request!\n\n"
                f"From: {callback.from_user.full_name}\n"
                f"Request: {request_service.get_request(request_id)['description']}\n\n"
                f"Can you help with this request?"
            )
            
            keyboard = get_helper_response_keyboard(request_id, requester_id)
            await callback.bot.send_message(
                chat_id=helper_id,
                text=helper_message,
                reply_markup=keyboard
            )

            # Update match status
            await update_match_status(
                request_id,
                helper_id,
                "pending",
                introducer_id=callback.from_user.id
            )

            await callback.answer("Introduction request sent to helper")
        else:
            # Update match status
            await update_match_status(
                request_id,
                helper_id,
                "declined",
                introducer_id=callback.from_user.id
            )

            # Notify requester
            requester_message = (
                f"Your introduction request has been declined by {callback.from_user.full_name}"
            )
            await callback.bot.send_message(
                chat_id=requester_id,
                text=requester_message
            )

            await callback.answer("Response sent")

    except Exception as e:
        logger.error(f"Error handling introducer response: {e}")
        await callback.answer("An error occurred")

async def log_request_match(
    request_id: str,
    helper_id: int,
    introducer_id: Optional[int] = None
) -> None:
    """
    Log a request match in the database.
    
    Args:
        request_id: The request ID
        helper_id: The Telegram ID of the helper
        introducer_id: Optional Telegram ID of the introducer
    """
    try:
        data = {
            "request_id": request_id,
            "suggested_user_id": helper_id,
            "status": "pending"
        }
        
        if introducer_id:
            data["introducer_user_id"] = introducer_id

        await supabase_client.table("request_matches_log").insert(data).execute()

    except Exception as e:
        logger.error(f"Error logging request match: {e}")
        raise

async def update_match_status(
    request_id: str,
    helper_id: int,
    status: str,
    introducer_id: Optional[int] = None
) -> None:
    """
    Update the status of a request match.
    
    Args:
        request_id: The request ID
        helper_id: The Telegram ID of the helper
        status: The new status
        introducer_id: Optional Telegram ID of the introducer
    """
    try:
        query = supabase_client.table("request_matches_log").update(
            {"status": status}
        ).match({
            "request_id": request_id,
            "suggested_user_id": helper_id
        })
        
        if introducer_id:
            query = query.match({"introducer_user_id": introducer_id})

        await query.execute()

    except Exception as e:
        logger.error(f"Error updating match status: {e}")
        raise

# Register handlers
router.callback_query.register(
    handle_ask_for_help,
    F.data.startswith("ask_help_")
)

router.callback_query.register(
    handle_helper_response,
    F.data.startswith(("accept_intro_", "decline_intro_"))
)

router.callback_query.register(
    handle_introducer_response,
    F.data.startswith(("facilitate_intro_", "decline_facilitate_"))
) 