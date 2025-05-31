from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from ..services.user_service import UserService
from ..services.connection_service import ConnectionService
from ..config import get_bot_username
from ..services.graph_service import GraphService
from ..services.supabase_client import SupabaseClient
from ..states.connection_states import ConnectionTrustStates
from ..keyboards.connections_keyboards import get_connection_type_keyboard, get_trust_score_keyboard, get_connection_list_keyboard, get_connection_stats_keyboard
import logging
from typing import Dict, Any

# Create router for connection handlers
router = Router()

# Initialize services
supabase_client = SupabaseClient()
user_service = UserService()
connection_service = ConnectionService()
graph_service = GraphService(supabase_client)

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
        # Generate invite link using Telegram ID
        bot_username = get_bot_username()
        invite_link = f"https://t.me/{bot_username}?start=invite_{user['telegram_id']}"
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
        # Generate invite link using Telegram ID
        bot_username = get_bot_username()
        invite_link = f"https://t.me/{bot_username}?start=invite_{user['telegram_id']}"
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
async def handle_deep_link(message: Message, state: FSMContext):
    logger.info(f"Processing deep link message: {message.text}")
    
    try:
        # Extract inviter ID from deep link
        parts = message.text.split(maxsplit=1)
        args = parts[1] if len(parts) > 1 else ""
        logger.info(f"Extracted args: {args}")
        if not args or not args.startswith("invite_"):
            logger.info("No invite args found")
            return
        inviter_id = args.split("invite_")[1]
        logger.info(f"Extracted inviter ID: {inviter_id}")
        
        # Get inviter and invitee data
        inviter = await graph_service._client.fetch_user_by_telegram_id(int(inviter_id))
        invitee = await user_service.get_or_create_user(message.from_user.id)
        
        if not inviter or not invitee:
            logger.error(f"User not found: inviter={inviter}, invitee={invitee}")
            await message.answer("❌ Error: User not found")
            return
        # Check if connection already exists
        existing_connection = await graph_service.get_connection(
            inviter['id'],
            invitee['id']
        )
        if existing_connection:
            logger.info(f"Connection already exists between {inviter['id']} and {invitee['id']}")
            await message.answer(
                f"✅ You are already connected with {inviter.get('name', 'this user')}!"
            )
            return
        # Store user IDs in state
        await state.update_data(
            user1_id=inviter['id'],
            user2_id=invitee['id']
        )
        # Set initial state
        await state.set_state(ConnectionTrustStates.connection_type)
        # Send connection type keyboard
        await message.answer(
            f"Как вы знаете {inviter.get('name', 'this person')}?\nПожалуйста, выберите тип связи:",
            reply_markup=get_connection_type_keyboard()
        )
        logger.info("Sent connection type keyboard")
    except Exception as e:
        logger.error(f"Error in handle_deep_link: {e}", exc_info=True)
        await message.answer("❌ Error processing invite. Please try again later")

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
        logger.info(f"Processing connection type selection: {callback.data}")
        
        # Extract connection type from callback data
        connection_type = callback.data.replace("conn_type_", "")
        logger.info(f"Selected connection type: {connection_type}")
        
        # Validate connection type
        if not graph_service.validate_connection_type(connection_type):
            logger.error(f"Invalid connection type: {connection_type}")
            await callback.answer("Invalid connection type selected.")
            return
            
        # Store connection type in state
        await state.update_data(connection_type=connection_type)
        logger.info(f"Stored connection type in state: {connection_type}")
        
        # Move to trust score state
        await state.set_state(ConnectionTrustStates.trust_score)
        logger.info("Set state to trust_score")
        
        # Send trust score keyboard
        await callback.message.edit_text(
            "What's your level of trust with this person?",
            reply_markup=get_trust_score_keyboard()
        )
        logger.info("Sent trust score keyboard")
        
    except Exception as e:
        logger.error(f"Error processing connection type: {e}", exc_info=True)
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
        logger.info(f"Processing trust score selection: {callback.data}")
        
        # Extract trust score from callback data
        trust_score = int(callback.data.replace("trust_score_", ""))
        logger.info(f"Selected trust score: {trust_score}")
        
        # Validate trust score
        if not graph_service.validate_trust_score(trust_score):
            logger.error(f"Invalid trust score: {trust_score}")
            await callback.answer("Invalid trust score selected.")
            return
            
        # Get all data from state
        data = await state.get_data()
        logger.info(f"Got data from state: {data}")
        
        user1_id = data['user1_id']
        user2_id = data['user2_id']
        connection_type = data['connection_type']
        
        # Create connection with selected details
        connection = await graph_service.create_connection(
            user1_id=user1_id,
            user2_id=user2_id,
            connection_type=connection_type,
            trust_score=trust_score,
            status="active"
        )
        logger.info(f"Created connection: {connection}")
        
        if connection:
            # Clear state
            await state.clear()
            logger.info("Cleared state")
            
            # Send success message
            await callback.message.edit_text(
                "✅ Connection created successfully! You can now view your connections using /myconnections"
            )
            logger.info("Sent success message")
        else:
            logger.error("Failed to create connection")
            await callback.message.edit_text(
                "❌ Error creating connection. Please try again later."
            )
            
    except Exception as e:
        logger.error(f"Error processing trust score: {e}", exc_info=True)
        await callback.message.edit_text(
            "Sorry, there was an error. Please try again later."
        )
    finally:
        await callback.answer()

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

@router.callback_query(lambda c: c.data == "my_connections")
async def handle_my_connections_button(callback: CallbackQuery):
    """Handle My Connections button click."""
    try:
        # Get user data
        user = await user_service.get_or_create_user(callback.from_user.id)
        if not user:
            await callback.answer("❌ Error: User not found", show_alert=True)
            return
            
        # Get connections (first page)
        result = await graph_service.get_friends(
            telegram_id=callback.from_user.id,
            page=1,
            per_page=10
        )
        
        if not result['connections']:
            await callback.message.answer(
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
        await callback.message.answer(
            connections_text,
            parse_mode="Markdown",
            reply_markup=get_connection_list_keyboard(
                page=result['page'],
                total_pages=result['total_pages']
            )
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing connections: {e}")
        await callback.answer("❌ Error showing connections", show_alert=True)

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