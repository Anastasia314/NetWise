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
from netwise_bot.services.user_service import user_service, UserService
from netwise_bot.services.request_service import request_service, RequestService
from netwise_bot.keyboards.interaction_keyboards import (
    get_helper_response_keyboard,
    get_introducer_response_keyboard,
    get_help_response_keyboard
)
from netwise_bot.services.notification_service import NotificationService
from netwise_bot.utils.constants import POINTS_PER_HELP

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
    state: FSMContext
) -> None:
    """
    Handle the initial "Ask for help" button click.
    
    Args:
        callback: The callback query
        state: The FSM context
    """
    try:
        logger.info(f"Received ask for help callback: data={callback.data}")
        
        # Extract helper UUID and match score from callback data (remove 'ah_' prefix)
        parts = callback.data[3:].split('_')  # Remove 'ah_' prefix and split by '_'
        helper_uuid = parts[0]
        match_score = int(parts[1]) if len(parts) > 1 else 0
        logger.info(f"Extracted helper_uuid={helper_uuid}, match_score={match_score}")
        
        # Get helper's Telegram ID
        helper = await supabase_client.get_user_by_id(helper_uuid)
        if not helper:
            logger.error(f"Helper not found for uuid={helper_uuid}")
            await callback.answer("Helper not found")
            return
        helper_telegram_id = helper['telegram_id']
        logger.info(f"Found helper: uuid={helper_uuid}, telegram_id={helper_telegram_id}")
        
        # Get requester's UUID
        requester_telegram_id = callback.from_user.id
        logger.info(f"Requester telegram_id={requester_telegram_id}")
        
        requester = await supabase_client.fetch_user_by_telegram_id(requester_telegram_id)
        if not requester:
            logger.error(f"Requester not found for telegram_id={requester_telegram_id}")
            await callback.answer("Requester not found")
            return
        requester_uuid = requester['id']
        logger.info(f"Found requester: uuid={requester_uuid}")
        
        # Get last active request
        request = await request_service.get_last_request_by_user(requester_telegram_id)
        if not request:
            logger.error(f"Request not found for requester_telegram_id={requester_telegram_id}")
            await callback.answer("Request not found")
            return
        request_id = request["id"]
        logger.info(f"Found request: id={request_id}")
        
        # Get connection type between users using UUIDs
        connection_type = await user_service.get_connection_type(
            requester_uuid,
            helper_uuid
        )
        logger.info(f"Connection type between users: {connection_type}")
        
        if connection_type == "direct":
            logger.info("Handling direct connection")
            await handle_direct_connection(
                callback,
                request,
                helper_uuid,
                helper_telegram_id,
                requester_uuid,
                requester_telegram_id,
                match_score
            )
        elif connection_type == "indirect":
            logger.info("Handling indirect connection")
            await handle_indirect_connection(
                callback,
                state,
                request,
                helper_uuid,
                helper_telegram_id,
                requester_uuid,
                requester_telegram_id,
                match_score
            )
        else:
            logger.warning(f"No connection found between users: requester={requester_telegram_id}, helper={helper_telegram_id}")
            await callback.answer("No connection found between users")
    except Exception as e:
        logger.error(f"Error handling ask for help: {e}", exc_info=True)
        await callback.answer("An error occurred")

async def handle_direct_connection(
    callback: CallbackQuery,
    request: dict,
    helper_uuid: str,
    helper_telegram_id: int,
    requester_uuid: str,
    requester_telegram_id: int,
    match_score: int
) -> None:
    """
    Handle direct connection between users.
    
    Args:
        callback: The callback query
        request: The request details
        helper_uuid: UUID of the helper
        helper_telegram_id: Telegram ID of the helper
        requester_uuid: UUID of the requester
        requester_telegram_id: Telegram ID of the requester
        match_score: The match score for this helper
    """
    try:
        # Log the match (используем UUID)
        await log_request_match(request["id"], helper_uuid, match_score=match_score)
        
        # Get requester's name
        requester = await supabase_client.get_user_by_id(requester_uuid)
        if not requester:
            raise Exception(f"Requester not found for uuid={requester_uuid}")
        requester_name = requester.get('name', 'Unknown User')
        
        # Send message to helper (используем Telegram ID)
        helper_message = (
            f"🔔 New help request!\n\n"
            f"From: {requester_name}\n"
            f"Request: {request['description_text']}\n\n"
            f"Can you help with this request?"
        )
        keyboard = get_helper_response_keyboard(request["id"], requester_telegram_id)
        await callback.bot.send_message(
            chat_id=helper_telegram_id,
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
    helper_uuid: str,
    helper_telegram_id: int,
    requester_uuid: str,
    requester_telegram_id: int,
    match_score: int
) -> None:
    """
    Handle indirect connection between users.
    
    Args:
        callback: The callback query
        state: The FSM context
        request: The request details
        helper_uuid: UUID of the helper
        helper_telegram_id: Telegram ID of the helper
        requester_uuid: UUID of the requester
        requester_telegram_id: Telegram ID of the requester
        match_score: The match score for this helper
    """
    try:
        # Get introducer (используем Telegram ID)
        introducer = await user_service.get_common_connection(
            requester_telegram_id,
            helper_telegram_id
        )
        if not introducer:
            await callback.answer("No common connection found")
            return
        introducer_telegram_id = introducer['telegram_id']
        introducer_uuid = introducer['id']
        
        # Get requester's name
        requester = await supabase_client.get_user_by_id(requester_uuid)
        if not requester:
            raise Exception(f"Requester not found for uuid={requester_uuid}")
        requester_name = requester.get('name', 'Unknown User')
        
        # Log the match (используем UUID)
        await log_request_match(
            request["id"],
            helper_uuid,
            introducer_id=introducer_uuid,
            match_score=match_score
        )
        
        # Send message to introducer (используем Telegram ID)
        introducer_message = (
            f"🔔 Introduction request!\n\n"
            f"From: {requester_name}\n"
            f"To: {helper_telegram_id}\n"
            f"Request: {request['description_text']}\n\n"
            f"Would you like to facilitate this introduction?"
        )
        keyboard = get_introducer_response_keyboard(
            request["id"],
            requester_telegram_id,
            helper_telegram_id
        )
        await callback.bot.send_message(
            chat_id=introducer_telegram_id,
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
            "helper_accepted" if accepted else "helper_declined"
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
    helper_uuid: str,
    introducer_id: Optional[str] = None,
    match_score: int = 0
) -> None:
    """
    Log a request match in the database.
    
    Args:
        request_id: The request ID
        helper_uuid: UUID of the helper
        introducer_id: Optional UUID of the introducer
        match_score: The match score for this helper
    """
    try:
        result = await supabase_client.log_request_match(
            request_id=request_id,
            suggested_user_uuid=helper_uuid,
            introducer_user_uuid=introducer_id,
            match_score=match_score
        )
        if not result:
            raise Exception("Failed to log request match")

    except Exception as e:
        logger.error(f"Error logging request match: {e}")
        raise

async def update_match_status(
    request_id: str,
    helper_id: int,
    status: str,
    introducer_id: Optional[str] = None
) -> None:
    """
    Update the status of a request match.
    
    Args:
        request_id: The request ID
        helper_id: The Telegram ID of the helper
        status: The new status
        introducer_id: Optional UUID of the introducer
    """
    try:
        # Get helper's UUID
        helper = await supabase_client.fetch_user_by_telegram_id(helper_id)
        if not helper:
            raise Exception(f"Helper not found for telegram_id={helper_id}")
        helper_uuid = helper['id']

        result = await supabase_client.update_request_match_status(
            request_id=request_id,
            suggested_user_uuid=helper_uuid,
            status=status,
            introducer_user_uuid=introducer_id
        )
        if not result:
            raise Exception("Failed to update match status")

    except Exception as e:
        logger.error(f"Error updating match status: {e}")
        raise

# Register handlers
router.callback_query.register(
    handle_ask_for_help,
    F.data.startswith("ah_")  # Only handle callbacks that start with "ah_"
)

router.callback_query.register(
    handle_introducer_response,
    F.data.startswith(("facilitate_intro_", "decline_facilitate_"))
)

# Add new handler for helper responses with parameter extraction
@router.callback_query(F.data.startswith(("accept_intro_", "decline_intro_")))
async def handle_helper_response_callback(callback: CallbackQuery):
    """
    Handle helper's response to a help request.
    Extracts parameters from callback data and calls handle_helper_response.
    """
    try:
        # Extract parameters from callback data
        # Format: accept_intro_{request_id}_{requester_id} or decline_intro_{request_id}_{requester_id}
        parts = callback.data.split('_')
        request_id = parts[2]
        requester_id = int(parts[3])
        accepted = parts[0] == "accept"
        
        await handle_helper_response(callback, request_id, requester_id, accepted)
    except Exception as e:
        logger.error(f"Error handling helper response callback: {e}")
        await callback.answer("An error occurred")

@router.callback_query(F.data.startswith("offer_help_"))
async def handle_help_offer(callback: CallbackQuery, request_service: RequestService, 
                          user_service: UserService, notification_service: NotificationService):
    """Handle when a user offers to help with a request."""
    try:
        # Parse callback data
        _, request_id, requester_id = callback.data.split("_")
        helper_id = callback.from_user.id

        # Update request status
        success = await request_service.update_request_status(request_id, "pending_help")
        if not success:
            await callback.answer("Извините, произошла ошибка. Попробуйте позже.")
            return

        # Notify requester
        await notification_service.notify_help_offer(helper_id, int(requester_id), request_id)

        # Add social points to helper
        await user_service.add_social_points(helper_id, POINTS_PER_HELP)

        # Log activity
        await user_service.log_activity(
            helper_id,
            "helped_on_request",
            request_id,
            POINTS_PER_HELP
        )

        await callback.answer("Спасибо за готовность помочь! Запросчик будет уведомлен.")
        await callback.message.edit_reply_markup(reply_markup=None)

    except Exception as e:
        logger.error(f"Error handling help offer: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("accept_help_"))
async def handle_help_acceptance(callback: CallbackQuery, request_service: RequestService,
                               notification_service: NotificationService):
    """Handle when a requester accepts help."""
    try:
        # Parse callback data
        _, request_id, helper_id = callback.data.split("_")
        requester_id = callback.from_user.id

        # Update request status
        success = await request_service.update_request_status(request_id, "help_accepted")
        if not success:
            await callback.answer("Извините, произошла ошибка. Попробуйте позже.")
            return

        # Notify helper
        await notification_service.notify_help_accepted(int(helper_id), requester_id, request_id)

        await callback.answer("Спасибо! Помощник будет уведомлен.")
        await callback.message.edit_reply_markup(reply_markup=None)

    except Exception as e:
        logger.error(f"Error handling help acceptance: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("decline_help_"))
async def handle_help_decline(callback: CallbackQuery, request_service: RequestService):
    """Handle when a requester declines help."""
    try:
        # Parse callback data
        _, request_id, helper_id = callback.data.split("_")

        # Update request status back to open
        success = await request_service.update_request_status(request_id, "open")
        if not success:
            await callback.answer("Извините, произошла ошибка. Попробуйте позже.")
            return

        await callback.answer("Вы отклонили предложение помощи.")
        await callback.message.edit_reply_markup(reply_markup=None)

    except Exception as e:
        logger.error(f"Error handling help decline: {e}")
        await callback.answer("Произошла ошибка. Попробуйте позже.") 