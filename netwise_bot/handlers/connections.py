from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..services.user_service import UserService
from ..services.connection_service import ConnectionService
from ..config import get_bot_username
import logging

# Create router for connection handlers
router = Router()

# Initialize services
user_service = UserService()
connection_service = ConnectionService()

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