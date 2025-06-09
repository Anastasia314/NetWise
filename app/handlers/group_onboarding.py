from aiogram import Router, F, Bot
from aiogram.types import ChatMemberUpdated, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
import logging
import asyncio

logger = logging.getLogger(__name__)

router = Router()

def get_bot_link_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with bot link button"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 Открыть бота",
                    url="https://t.me/smart_networking_bot"
                )
            ]
        ]
    )
    return keyboard

@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_user_join(event: ChatMemberUpdated, bot: Bot):
    """Handle new user joining the chat
    
    Args:
        event: ChatMemberUpdated event with new member info
        bot: Bot instance for sending messages
    """
    try:
        # Get new member info
        new_member = event.new_chat_member.user
        
        # Create welcome message
        welcome_text = (
            f"👋 Привет, {new_member.mention_html()}!\n\n"
            "Добро пожаловать в чат! Я помогу тебе создать профиль для нетворкинга.\n"
            "Нажми на кнопку ниже, чтобы начать."
        )
        
        # Send welcome message with keyboard
        msg = await bot.send_message(
            chat_id=event.chat.id,
            text=welcome_text,
            reply_markup=get_bot_link_keyboard(),
            parse_mode="HTML"
        )

        await asyncio.sleep(20)
        await bot.delete_message(chat_id=event.chat.id, message_id=msg.message_id)
        
    except Exception as e:
        logger.error(f"Error in on_user_join: {e}", exc_info=True)
        # Try to send error message to chat
        try:
            await bot.send_message(
                chat_id=event.chat.id,
                text="❌ Произошла ошибка при обработке нового участника. Пожалуйста, попробуйте позже."
            )
        except:
            pass 