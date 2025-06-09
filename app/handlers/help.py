from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Create router
router = Router()

@router.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = """
🤖 <b>NetWise Bot – Помощь</b>

Доступные команды:

/myprofile – Создать или обновить свой профиль  
/search – Найти людей по тегам и интересам  
/help – Показать это сообщение

<b>Как пользоваться:</b>

1. Начните с команды <b>/myprofile</b> – укажите о себе, чем занимаетесь, и добавьте теги.
2. После этого используйте <b>/search</b> – бот подберёт релевантных людей по тегам.
3. В результатах поиска жмите <b>💬 Написать</b>, чтобы связаться напрямую.

<b>Про теги:</b>
- Можно выбрать до 3 личных тегов и до 3 поисковых.
"""
    await message.answer(help_text, parse_mode="HTML")