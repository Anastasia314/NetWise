from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from ..services.user_service import UserService
from ..services.connection_service import ConnectionService
from ..config import get_bot_username
from ..services.graph_service import GraphService
from ..states.connection_states import ConnectionTrustStates
from ..keyboards.connections_keyboards import get_connection_type_keyboard, get_trust_score_keyboard, get_connection_list_keyboard, get_connection_stats_keyboard
import logging
from typing import Dict, Any

# Create router for connection handlers
router = Router()

# Initialize services
user_service = UserService()
connection_service = ConnectionService()
graph_service = GraphService()

# Get logger
logger = logging.getLogger(__name__)

@router.callback_query(lambda c: c.data == "generate_invite")
async def generate_invite_link(callback: CallbackQuery):
    """Generate a unique invite link for the user."""
    try:
        # Get user data
        user = await user_service.get_or_create_user(callback.from_user.id)
        if not user:
            await callback.answer("❌ Error: User not found", show_alert=True)
            return
            
        # Generate invite link
        bot_username = get_bot_username()
        invite_link = f"https://t.me/{bot_username}?start=invite_{user['id']}"
        
        # Create keyboard with copy button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_invite")]
        ])
        
        await callback.message.answer(
            f"🔗 *Your Invite Link*\n\n"
            f"Share this link with others to connect with them:\n"
            f"`{invite_link}`\n\n"
            f"The person who clicks this link will be automatically connected to you.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error generating invite link: {e}")
        await callback.answer("❌ Error generating invite link", show_alert=True)

@router.callback_query(lambda c: c.data == "copy_invite")
async def copy_invite_link(callback: CallbackQuery):
    """Copy invite link to clipboard."""
    try:
        # Get user data
        user = await user_service.get_or_create_user(callback.from_user.id)
        if not user:
            await callback.answer("❌ Error: User not found", show_alert=True)
            return
            
        # Generate invite link
        bot_username = get_bot_username()
        invite_link = f"https://t.me/{bot_username}?start=invite_{user['id']}"
        
        # Send link as a separate message for easy copying
        await callback.message.answer(
            f"🔗 *Click to copy:*\n`{invite_link}`",
            parse_mode="Markdown"
        )
        await callback.answer("✅ Link sent as a separate message for easy copying")
        
    except Exception as e:
        logger.error(f"Error copying invite link: {e}")
        await callback.answer("❌ Error copying invite link", show_alert=True)

@router.message(CommandStart(deep_link=True))
async def handle_invite_link(message: Message):
    """Handle invite link clicks."""
    try:
        # Extract inviter ID from deep link
        args = message.get_args().split('_')
        if len(args) != 2 or args[0] != 'invite':
            return
            
        inviter_id = args[1]
        
        # Get inviter's data
        inviter = await user_service.get_user_by_id(inviter_id)
        if not inviter:
            await message.answer("❌ Invalid invite link")
            return
            
        # Get or create current user
        current_user = await user_service.get_or_create_user(message.from_user.id)
        if not current_user:
            await message.answer("❌ Error creating user profile")
            return
            
        # Create connection
        success = await connection_service.create_connection(
            user1_id=inviter_id,
            user2_id=current_user['id'],
            connection_type="invite",
            trust_score=10
        )
        
        if success:
            # Notify both users
            await message.answer(
                f"✅ Successfully connected with {inviter.get('name', 'Unknown')}!"
            )
            
            # Notify inviter (if they're online)
            try:
                await message.bot.send_message(
                    chat_id=inviter['telegram_id'],
                    text=f"✅ {current_user.get('name', 'Someone')} has joined through your invite link!"
                )
            except Exception as e:
                logger.error(f"Error notifying inviter: {e}")
        else:
            await message.answer("❌ Error creating connection")
            
    except Exception as e:
        logger.error(f"Error handling invite link: {e}")
        await message.answer("❌ Error processing invite link")

@router.callback_query(lambda c: c.data == "my_connections")
async def show_connections(callback: CallbackQuery):
    """Show user's connections."""
    try:
        # Get user data
        user = await user_service.get_or_create_user(callback.from_user.id)
        if not user:
            await callback.answer("❌ Error: User not found", show_alert=True)
            return
            
        # Get connections
        connections = await connection_service.get_user_connections(user['id'])
        
        if not connections:
            await callback.message.answer(
                "👥 *Your Connections*\n\n"
                "You don't have any connections yet.\n"
                "Use the invite link to connect with others!",
                parse_mode="Markdown"
            )
            return
            
        # Format connections list
        connections_text = "👥 *Your Connections:*\n\n"
        for conn in connections:
            other_user_id = conn['user2_id'] if conn['user1_id'] == user['id'] else conn['user1_id']
            other_user = await user_service.get_user_by_id(other_user_id)
            
            if other_user:
                connections_text += (
                    f"• *{other_user.get('name', 'Unknown')}*\n"
                    f"  Role: {other_user.get('role', 'Not set')}\n"
                    f"  Industry: {other_user.get('industry', 'Not set')}\n"
                    f"  Trust Score: {conn.get('trust_score', 0)}\n\n"
                )
        
        await callback.message.answer(
            connections_text,
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing connections: {e}")
        await callback.answer("❌ Error showing connections", show_alert=True)

@router.callback_query(F.data.startswith("set_connection_details_"))
async def start_connection_details(
    callback: types.CallbackQuery,
    state: FSMContext
):
    """Start the connection details flow."""
    try:
        # Extract user IDs from callback data
        _, user1_id, user2_id = callback.data.split("_")
        
        # Store user IDs in state
        await state.update_data(
            user1_id=user1_id,
            user2_id=user2_id
        )
        
        # Set initial state
        await state.set_state(ConnectionTrustStates.connection_type)
        
        # Send connection type keyboard
        await callback.message.edit_text(
            "How do you know this person?",
            reply_markup=get_connection_type_keyboard()
        )
        
    except Exception as e:
        print(f"Error starting connection details: {e}")
        await callback.message.edit_text(
            "Sorry, there was an error. Please try again later."
        )
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("conn_type_"))
async def process_connection_type(
    callback: types.CallbackQuery,
    state: FSMContext
):
    """Process connection type selection."""
    try:
        # Extract connection type from callback data
        connection_type = callback.data.replace("conn_type_", "")
        
        # Validate connection type
        if not graph_service.validate_connection_type(connection_type):
            await callback.answer("Invalid connection type selected.")
            return
            
        # Store connection type in state
        await state.update_data(connection_type=connection_type)
        
        # Move to trust score state
        await state.set_state(ConnectionTrustStates.trust_score)
        
        # Send trust score keyboard
        await callback.message.edit_text(
            "What's your level of trust with this person?",
            reply_markup=get_trust_score_keyboard()
        )
        
    except Exception as e:
        print(f"Error processing connection type: {e}")
        await callback.message.edit_text(
            "Sorry, there was an error. Please try again later."
        )
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("trust_score_"))
async def process_trust_score(
    callback: types.CallbackQuery,
    state: FSMContext
):
    """Process trust score selection and complete the flow."""
    try:
        # Extract trust score from callback data
        trust_score = int(callback.data.replace("trust_score_", ""))
        
        # Validate trust score
        if not graph_service.validate_trust_score(trust_score):
            await callback.answer("Invalid trust score selected.")
            return
            
        # Get all data from state
        data = await state.get_data()
        user1_id = data['user1_id']
        user2_id = data['user2_id']
        connection_type = data['connection_type']
        
        # Update connection in database
        connection = await graph_service.update_connection_details(
            user1_id=user1_id,
            user2_id=user2_id,
            connection_type=connection_type,
            trust_score=trust_score
        )
        
        if connection:
            # Get user names for the message
            user1 = await user_service.get_profile(int(user1_id))
            user2 = await user_service.get_profile(int(user2_id))
            user1_name = user1.get('name', 'User') if user1 else 'User'
            user2_name = user2.get('name', 'User') if user2 else 'User'
            
            # Send success message
            await callback.message.edit_text(
                f"Connection details updated successfully!\n\n"
                f"Connection between {user1_name} and {user2_name}:\n"
                f"Type: {connection_type.replace('_', ' ').title()}\n"
                f"Trust Level: {trust_score}"
            )
        else:
            await callback.message.edit_text(
                "Sorry, there was an error updating the connection details. "
                "Please try again later."
            )
            
    except ValueError as e:
        await callback.message.edit_text(str(e))
    except Exception as e:
        print(f"Error processing trust score: {e}")
        await callback.message.edit_text(
            "Sorry, there was an error. Please try again later."
        )
    finally:
        await callback.answer()
        await state.clear()

@router.message(Command("myconnections"))
async def show_my_connections(message: Message):
    """Show user's connections with filtering and pagination."""
    try:
        # Get user data
        user = await user_service.get_or_create_user(message.from_user.id)
        if not user:
            await message.answer("❌ Error: User not found")
            return
            
        # Get connections (first page)
        result = await graph_service.get_friends(
            telegram_id=message.from_user.id,
            page=1,
            per_page=10
        )
        
        if not result['connections']:
            await message.answer(
                "👥 *Your Connections*\n\n"
                "You don't have any connections yet.\n"
                "Use the invite link to connect with others!",
                parse_mode="Markdown"
            )
            return
            
        # Format connections list
        connections_text = "👥 *Your Connections:*\n\n"
        for conn in result['connections']:
            user_details = conn.get('user_details', {})
            connections_text += (
                f"• *{user_details.get('name', 'Unknown')}*\n"
                f"  Role: {user_details.get('role', 'Not set')}\n"
                f"  Industry: {user_details.get('industry', 'Not set')}\n"
                f"  Trust Score: {conn.get('trust_score', 0)}\n"
                f"  Connection Type: {conn.get('connection_type', 'Unknown').replace('_', ' ').title()}\n\n"
            )
            
        # Add pagination info
        connections_text += f"\nPage {result['page']} of {result['total_pages']}"
        
        # Send message with keyboard
        await message.answer(
            connections_text,
            parse_mode="Markdown",
            reply_markup=get_connection_list_keyboard(
                page=result['page'],
                total_pages=result['total_pages']
            )
        )
        
    except Exception as e:
        logger.error(f"Error showing connections: {e}")
        await message.answer("❌ Error showing connections")

@router.callback_query(F.data.startswith("filter_"))
async def handle_connection_filter(callback: CallbackQuery):
    """Handle connection list filtering."""
    try:
        # Extract filter from callback data
        filter_type = callback.data.replace("filter_", "")
        
        # Parse filter parameters
        trust_score = None
        if filter_type.startswith("trust_"):
            trust_score = int(filter_type.split("_")[1])
            
        # Get connections with filter
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            trust_score=trust_score,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_connections(
            callback.message,
            result,
            current_filter=callback.data
        )
        
    except Exception as e:
        logger.error(f"Error handling filter: {e}")
        await callback.answer("❌ Error applying filter")
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("sort_"))
async def handle_connection_sort(callback: CallbackQuery):
    """Handle connection list sorting."""
    try:
        # Extract sort from callback data
        sort_type = callback.data.replace("sort_", "")
        
        # Map sort type to field
        sort_map = {
            "name": "name",
            "trust": "trust_score",
            "date": "created_at"
        }
        sort_by = sort_map.get(sort_type, "name")
        
        # Get connections with sort
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            sort_by=sort_by,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_connections(
            callback.message,
            result,
            current_sort=callback.data
        )
        
    except Exception as e:
        logger.error(f"Error handling sort: {e}")
        await callback.answer("❌ Error applying sort")
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("page_"))
async def handle_connection_page(callback: CallbackQuery):
    """Handle connection list pagination."""
    try:
        # Extract page number from callback data
        page = int(callback.data.replace("page_", ""))
        
        # Get connections for page
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            page=page
        )
        
        # Format and send updated list
        await format_and_send_connections(
            callback.message,
            result
        )
        
    except Exception as e:
        logger.error(f"Error handling pagination: {e}")
        await callback.answer("❌ Error changing page")
    finally:
        await callback.answer()

@router.callback_query(F.data == "refresh_connections")
async def handle_connection_refresh(callback: CallbackQuery):
    """Handle connection list refresh."""
    try:
        # Get fresh connections
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_connections(
            callback.message,
            result
        )
        
    except Exception as e:
        logger.error(f"Error refreshing connections: {e}")
        await callback.answer("❌ Error refreshing list")
    finally:
        await callback.answer()

@router.callback_query(F.data == "connection_stats")
async def handle_connection_stats(callback: CallbackQuery):
    """Show connection statistics."""
    try:
        # Get all connections for stats
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            per_page=1000  # Get all for stats
        )
        
        # Calculate statistics
        total_connections = result['total']
        trust_scores = [conn['trust_score'] for conn in result['connections']]
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0
        
        # Format stats message
        stats_text = (
            "📊 *Connection Statistics*\n\n"
            f"Total Connections: {total_connections}\n"
            f"Average Trust Score: {avg_trust:.1f}\n\n"
            "Trust Score Distribution:\n"
        )
        
        # Add trust score distribution
        for score in range(1, 4):
            count = trust_scores.count(score)
            percentage = (count / total_connections * 100) if total_connections else 0
            stats_text += f"Level {score}: {count} ({percentage:.1f}%)\n"
            
        # Send stats with keyboard
        await callback.message.edit_text(
            stats_text,
            parse_mode="Markdown",
            reply_markup=get_connection_stats_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await callback.answer("❌ Error showing statistics")
    finally:
        await callback.answer()

@router.callback_query(F.data == "back_to_connections")
async def handle_back_to_connections(callback: CallbackQuery):
    """Return to connection list from stats."""
    try:
        # Get connections
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            page=1
        )
        
        # Format and send updated list
        await format_and_send_connections(
            callback.message,
            result
        )
        
    except Exception as e:
        logger.error(f"Error returning to list: {e}")
        await callback.answer("❌ Error returning to list")
    finally:
        await callback.answer()

async def format_and_send_connections(
    message: Message,
    result: Dict[str, Any],
    current_filter: str = None,
    current_sort: str = None
):
    """Helper function to format and send connection list."""
    # Format connections list
    connections_text = "👥 *Your Connections:*\n\n"
    for conn in result['connections']:
        user_details = conn.get('user_details', {})
        connections_text += (
            f"• *{user_details.get('name', 'Unknown')}*\n"
            f"  Role: {user_details.get('role', 'Not set')}\n"
            f"  Industry: {user_details.get('industry', 'Not set')}\n"
            f"  Trust Score: {conn.get('trust_score', 0)}\n"
            f"  Connection Type: {conn.get('connection_type', 'Unknown').replace('_', ' ').title()}\n\n"
        )
        
    # Add pagination info
    connections_text += f"\nPage {result['page']} of {result['total_pages']}"
    
    # Update message with keyboard
    await message.edit_text(
        connections_text,
        parse_mode="Markdown",
        reply_markup=get_connection_list_keyboard(
            page=result['page'],
            total_pages=result['total_pages'],
            current_filter=current_filter,
            current_sort=current_sort
        )
    ) 