from aiogram import Router, F
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from app.keyboards.onboarding import get_onboarding_keyboard

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_user_join(event: ChatMemberUpdated):
    """Handle new user joining the chat
    
    Args:
        event: ChatMemberUpdated event with new member info
    """
    # Get new member info
    new_member = event.new_chat_member.user
    
    # Create welcome message
    welcome_text = (
        f"👋 Привет, {new_member.mention_html()}!\n\n"
        "Добро пожаловать в чат! Я помогу тебе создать профиль для нетворкинга.\n"
        "Нажми на кнопку ниже, чтобы начать."
    )
    
    # Send welcome message with keyboard
    await event.message.answer(
        text=welcome_text,
        reply_markup=get_onboarding_keyboard(),
        parse_mode="HTML"
    ) 