"""
Request handlers for managing user requests.
"""
import logging
from typing import Dict, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from netwise_bot.states.request_states import RequestStates
from netwise_bot.services.request_service import request_service
from netwise_bot.services.matching_service import matching_service
from netwise_bot.services.user_service import user_service
from netwise_bot.keyboards.request_keyboards import (
    get_request_confirmation_keyboard,
    get_request_cancellation_keyboard,
    get_ask_help_keyboard
)

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("newrequest"))
async def cmd_newrequest(message: Message, state: FSMContext):
    """
    Handle /newrequest command.
    Start the request creation flow.
    """
    try:
        # Check user's request quota
        success, message_text = await user_service.use_free_request(message.from_user.id)
        if not success:
            await message.answer(message_text)
            return

        # Set initial state
        await state.set_state(RequestStates.description)
        
        # Send prompt for request description
        await message.answer(
            "Please describe what kind of help you're looking for. "
            "Be specific about your needs and any relevant details.",
            reply_markup=get_request_cancellation_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in /newrequest command: {e}")
        await message.answer(
            "Sorry, there was an error starting your request. Please try again."
        )

@router.message(RequestStates.description)
async def handle_request_description(message: Message, state: FSMContext):
    """
    Handle request description input.
    Store description and show confirmation keyboard.
    """
    try:
        # Store description in state
        await state.update_data(description=message.text)
        
        # Show confirmation keyboard
        await message.answer(
            "Here's your request description:\n\n"
            f"{message.text}\n\n"
            "Would you like to submit this request?",
            reply_markup=get_request_confirmation_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error handling request description: {e}")
        await message.answer(
            "Sorry, there was an error processing your request. Please try again.",
            reply_markup=get_request_cancellation_keyboard()
        )

@router.callback_query(F.data == "submit_request")
async def handle_request_submission(callback: CallbackQuery, state: FSMContext):
    """
    Handle request submission.
    Create request and find potential helpers.
    """
    try:
        # Get description from state
        data = await state.get_data()
        description = data.get('description')
        if not description:
            await callback.message.edit_text(
                "Sorry, your request description was lost. Please try again.",
                reply_markup=get_request_cancellation_keyboard()
            )
            return

        # Create request
        success, message_text, request_id = await request_service.create_request(
            callback.from_user.id,
            description
        )
        
        if not success:
            await callback.message.edit_text(
                message_text,
                reply_markup=get_request_cancellation_keyboard()
            )
            return

        # Find potential helpers
        potential_helpers = await matching_service.find_keyword_matches(
            description,
            callback.from_user.id
        )

        if not potential_helpers:
            await callback.message.edit_text(
                "Your request has been created! However, we couldn't find any "
                "potential helpers in your network at the moment. We'll notify "
                "you if someone becomes available to help."
            )
            return

        # Format and display potential helpers
        response_text = (
            "Your request has been created! Here are some people in your network "
            "who might be able to help:\n\n"
        )

        for i, helper in enumerate(potential_helpers[:5], 1):  # Show top 5 matches
            response_text += (
                f"{i}. {helper['name']}\n"
                f"   Connection: {helper['connection_type']}\n"
                f"   Trust Score: {helper['trust_score']}\n"
                f"   Match Score: {helper['score']}\n\n"
            )

        # Add keyboard with "Ask for help" buttons
        await callback.message.edit_text(
            response_text,
            reply_markup=get_ask_help_keyboard(request_id, potential_helpers[:5])
        )

    except Exception as e:
        logger.error(f"Error submitting request: {e}")
        await callback.message.edit_text(
            "Sorry, there was an error submitting your request. Please try again.",
            reply_markup=get_request_cancellation_keyboard()
        )
    finally:
        # Clear state
        await state.clear()

@router.callback_query(F.data == "cancel_request")
async def handle_request_cancellation(callback: CallbackQuery, state: FSMContext):
    """
    Handle request cancellation.
    Clear state and notify user.
    """
    try:
        await state.clear()
        await callback.message.edit_text(
            "Request creation cancelled. You can start a new request with /newrequest."
        )
    except Exception as e:
        logger.error(f"Error cancelling request: {e}")
        await callback.message.edit_text(
            "Sorry, there was an error cancelling your request. Please try again."
        ) 