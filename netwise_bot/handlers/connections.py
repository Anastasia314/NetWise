from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..services.graph_service import GraphService
from ..services.user_service import UserService
from ..config import get_bot_username

router = Router()

def get_invite_keyboard(invite_link: str) -> InlineKeyboardMarkup:
    """Create keyboard with invite link."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Share Invite Link", url=invite_link)]
        ]
    )

@router.message(Command("invite"))
async def handle_invite_command(message: types.Message, graph_service: GraphService, user_service: UserService):
    """Handle /invite command to generate and display invite link."""
    # Get user's Telegram ID
    telegram_id = message.from_user.id
    
    # Get user from database to ensure they exist
    user = await user_service.get_or_create_user(telegram_id, message.from_user.full_name)
    if not user:
        await message.answer("Sorry, there was an error processing your request. Please try again later.")
        return
        
    # Generate invite link
    invite_link = await graph_service.generate_invite_link(telegram_id)
    if not invite_link:
        await message.answer("Sorry, there was an error generating your invite link. Please try again later.")
        return
        
    # Create keyboard with invite link
    keyboard = get_invite_keyboard(invite_link)
    
    # Send message with invite link
    await message.answer(
        "Invite your friends to join NetWise! Share this link with them:\n\n"
        f"{invite_link}\n\n"
        "When they join through your link, you'll be automatically connected!",
        reply_markup=keyboard
    ) 