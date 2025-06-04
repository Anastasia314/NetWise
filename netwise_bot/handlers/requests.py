"""
Request handlers for managing user requests.
"""
import logging
from typing import Dict, List, Any
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from netwise_bot.states.request_states import RequestStates, RequestEditStates
from netwise_bot.services.request_service import request_service, RequestService
from netwise_bot.services.matching_service import matching_service
from netwise_bot.services.user_service import user_service
from netwise_bot.keyboards.request_keyboards import (
    get_request_confirmation_keyboard,
    get_request_cancellation_keyboard,
    get_ask_help_keyboard,
    get_request_list_keyboard,
    get_request_details_keyboard,
    get_request_edit_keyboard,
    get_request_delete_confirm_keyboard,
    get_request_stats_keyboard
)
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("newrequest"))
async def cmd_newrequest(message: Message, state: FSMContext):
    """
    Handle /newrequest command.
    Start the request creation flow.
    """
    try:
        # Check if user has free requests remaining
        success = await user_service.add_free_request(message.from_user.id)
        if not success:
            await message.answer("You have no free requests remaining. Please purchase more requests or wait for your monthly quota to reset.")
            return

        # Ask for request description
        await message.answer("Please describe your request in detail. What kind of help or connection are you looking for?")
        await state.set_state(RequestStates.description)

    except Exception as e:
        logger.error(f"Error in /newrequest command: {e}")
        await message.answer("An error occurred. Please try again later.")

@router.callback_query(F.data == "new_request")
async def handle_new_request_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle new request button callback.
    Start the request creation flow.
    """
    try:
        # Check if user has free requests remaining
        success = await user_service.add_free_request(callback.from_user.id)
        if not success:
            await callback.message.edit_text("You have no free requests remaining. Please purchase more requests or wait for your monthly quota to reset.")
            return

        # Ask for request description
        await callback.message.edit_text("Please describe your request in detail. What kind of help or connection are you looking for?")
        await state.set_state(RequestStates.description)

    except Exception as e:
        logger.error(f"Error in new request callback: {e}")
        await callback.message.edit_text("An error occurred. Please try again later.")

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

@router.message(Command("myrequests"))
async def show_my_requests(message: types.Message):
    """Show user's requests."""
    try:
        result = await request_service.get_user_requests(
            telegram_id=message.from_user.id,
            page=1
        )
        
        if not result["requests"]:
            await message.answer("У вас пока нет запросов.")
            return
            
        await format_and_send_requests(message, result)
        
    except Exception as e:
        logger.error(f"Error showing requests: {e}")
        await message.answer("Произошла ошибка при загрузке запросов. Попробуйте позже.")

async def format_and_send_requests(message: types.Message, result: Dict[str, Any]):
    """Format and send request list."""
    requests = result["requests"]
    page = result["page"]
    total_pages = result["total_pages"]
    
    text = f"📋 Ваши запросы (страница {page}/{total_pages}):\n\n"
    
    for req in requests:
        # Convert string dates to datetime objects if needed
        created_at = req["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        text += f"📝 {req['description_text'][:100]}...\n"
        text += f"📅 Создан: {created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"👥 Помощников: {req['helpers_count']}\n"
        text += f"💬 Предложений: {req['offers_count']}\n\n"
    
    keyboard = get_request_list_keyboard(requests, page, total_pages)
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("request_page_"))
async def handle_request_page(callback_query: types.CallbackQuery):
    """Handle request list pagination."""
    try:
        page = int(callback_query.data.split("_")[-1])
        result = await request_service.get_user_requests(
            telegram_id=callback_query.from_user.id,
            page=page
        )
        
        if result["requests"]:
            await format_and_send_requests(callback_query.message, result)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error handling request page: {e}")
        await callback_query.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(lambda c: c.data.startswith("request_details_"))
async def handle_request_details(callback_query: types.CallbackQuery):
    """Show request details."""
    try:
        request_id = callback_query.data.split("_")[-1]
        request = await request_service.get_request(request_id)
        
        if not request:
            await callback_query.answer("Запрос не найден.")
            return
            
        # Convert string dates to datetime objects if needed
        created_at = request['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        text = f"📝 Запрос:\n{request['description_text']}\n\n"
        text += f"📅 Создан: {created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"📊 Статус: {request['status']}\n"
        
        keyboard = get_request_details_keyboard(request_id)
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error showing request details: {e}")
        await callback_query.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(lambda c: c.data.startswith("request_edit_"))
async def handle_request_edit_start(callback_query: types.CallbackQuery, state: FSMContext):
    """Start request editing."""
    try:
        request_id = callback_query.data.split("_")[-1]
        request = await request_service.get_request(request_id)
        
        if not request:
            await callback_query.answer("Запрос не найден.")
            return
            
        await state.set_state(RequestEditStates.editing)
        await state.update_data(request_id=request_id)
        
        text = "✏️ Введите новый текст запроса:"
        keyboard = get_request_edit_keyboard(request_id)
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error starting request edit: {e}")
        await callback_query.answer("Произошла ошибка. Попробуйте позже.")

@router.message(RequestEditStates.editing)
async def handle_request_edit_save(message: types.Message, state: FSMContext):
    """Save edited request."""
    try:
        data = await state.get_data()
        request_id = data.get("request_id")
        
        if not request_id:
            await message.answer("Ошибка: не найден ID запроса.")
            return
            
        # Validate new description
        is_valid, error_msg = await request_service.validate_request_description(message.text)
        if not is_valid:
            await message.answer(error_msg)
            return
            
        # Update request
        success = await request_service.update_request(request_id, message.text)
        if not success:
            await message.answer("Не удалось обновить запрос. Попробуйте позже.")
            return
            
        await state.clear()
        await message.answer("✅ Запрос успешно обновлен!")
        
        # Show updated request
        request = await request_service.get_request(request_id)
        if not request:
            await message.answer("Ошибка: не удалось получить обновленный запрос.")
            return
            
        # Convert string dates to datetime objects if needed
        created_at = request['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        text = f"📝 Запрос:\n{request['description_text']}\n\n"
        text += f"📅 Создан: {created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"📊 Статус: {request['status']}\n"
        
        keyboard = get_request_details_keyboard(request_id)
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error saving request edit: {e}")
        await message.answer("Произошла ошибка при сохранении. Попробуйте позже.")
        await state.clear()

@router.callback_query(lambda c: c.data.startswith("request_delete_"))
async def handle_request_delete_start(callback_query: types.CallbackQuery):
    """Start request deletion."""
    try:
        request_id = callback_query.data.split("_")[-1]
        request = await request_service.get_request(request_id)
        
        if not request:
            await callback_query.answer("Запрос не найден.")
            return
            
        # Convert string dates to datetime objects if needed
        created_at = request['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        # Create a new message instead of editing the existing one
        text = f"⚠️ Вы уверены, что хотите удалить этот запрос?\n\n"
        text += f"📝 Запрос:\n{request['description_text']}\n\n"
        text += f"📅 Создан: {created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"📊 Статус: {request['status']}\n"
        
        keyboard = get_request_delete_confirm_keyboard(request_id)
        await callback_query.message.answer(text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error starting request deletion: {e}")
        await callback_query.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def handle_request_delete_confirm(callback_query: types.CallbackQuery):
    """Confirm and process request deletion."""
    try:
        request_id = callback_query.data.split("_")[-1]
        
        # Delete the confirmation message first
        await callback_query.message.delete()
        
        # Attempt to delete the request
        success = await request_service.delete_request(request_id)
        if not success:
            await callback_query.message.answer("Не удалось удалить запрос. Попробуйте позже.")
            return
            
        # Show success message
        await callback_query.message.answer("✅ Запрос успешно удален!")
        
        # Show updated request list
        result = await request_service.get_user_requests(
            telegram_id=callback_query.from_user.id,
            page=1
        )
        
        if result["requests"]:
            await format_and_send_requests(callback_query.message, result)
        else:
            await callback_query.message.answer("У вас больше нет запросов.")
            
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error confirming request deletion: {e}")
        await callback_query.message.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(lambda c: c.data == "back_to_list")
async def handle_back_to_list(callback_query: types.CallbackQuery):
    """Return to request list."""
    try:
        result = await request_service.get_user_requests(
            telegram_id=callback_query.from_user.id,
            page=1
        )
        
        if result["requests"]:
            await format_and_send_requests(callback_query.message, result)
        else:
            await callback_query.message.edit_text("У вас пока нет запросов.")
            
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error returning to list: {e}")
        await callback_query.answer("Произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("req_filter_"))
async def handle_request_filter(callback: CallbackQuery):
    """Handle request list filtering."""
    try:
        # Extract filter from callback data
        filter_type = callback.data.replace("req_filter_", "")
        
        # Get requests with filter
        result = await request_service.get_user_requests(
            telegram_id=callback.from_user.id,
            status=filter_type if filter_type != "all" else None,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_requests(
            callback.message,
            result,
            current_filter=callback.data
        )
        
    except Exception as e:
        logger.error(f"Error handling filter: {e}")
        await callback.answer("❌ Error applying filter")
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("req_sort_"))
async def handle_request_sort(callback: CallbackQuery):
    """Handle request list sorting."""
    try:
        # Extract sort from callback data
        sort_type = callback.data.replace("req_sort_", "")
        
        # Map sort type to field
        sort_map = {
            "date": "created_at",
            "status": "status"
        }
        sort_by = sort_map.get(sort_type, "created_at")
        
        # Get requests with sort
        result = await request_service.get_user_requests(
            telegram_id=callback.from_user.id,
            sort_by=sort_by,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_requests(
            callback.message,
            result,
            current_sort=callback.data
        )
        
    except Exception as e:
        logger.error(f"Error handling sort: {e}")
        await callback.answer("❌ Error applying sort")
    finally:
        await callback.answer()

@router.callback_query(F.data == "req_refresh")
async def handle_request_refresh(callback: CallbackQuery):
    """Handle request list refresh."""
    try:
        # Get fresh requests
        result = await request_service.get_user_requests(
            telegram_id=callback.from_user.id,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_requests(
            callback.message,
            result
        )
        
    except Exception as e:
        logger.error(f"Error refreshing requests: {e}")
        await callback.answer("❌ Error refreshing list")
    finally:
        await callback.answer()

@router.callback_query(F.data == "req_stats")
async def handle_request_stats(callback: CallbackQuery):
    """Show request statistics."""
    try:
        # Get statistics
        stats = await request_service.get_user_request_stats(
            telegram_id=callback.from_user.id
        )
        
        # Format stats message
        stats_text = (
            "📊 *Request Statistics*\n\n"
            f"Total Requests: {stats['total_requests']}\n"
            f"Open Requests: {stats['open_requests']}\n"
            f"Pending Requests: {stats['pending_requests']}\n"
            f"Active Requests: {stats['active_requests']}\n"
            f"Average Response Time: {stats['avg_response_time']} hours\n"
            f"Success Rate: {stats['success_rate']}%\n"
        )
        
        # Send stats with keyboard
        await callback.message.edit_text(
            stats_text,
            parse_mode="Markdown",
            reply_markup=get_request_stats_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await callback.answer("❌ Error showing statistics")
    finally:
        await callback.answer()

@router.callback_query(F.data == "req_back_to_list")
async def handle_back_to_list(callback: CallbackQuery):
    """Return to request list from details/stats."""
    try:
        # Get fresh requests
        result = await request_service.get_user_requests(
            telegram_id=callback.from_user.id,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_requests(
            callback.message,
            result
        )
        
    except Exception as e:
        logger.error(f"Error returning to list: {e}")
        await callback.answer("❌ Error returning to list")
    finally:
        await callback.answer() 