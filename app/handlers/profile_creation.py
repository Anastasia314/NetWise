from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from supabase import create_client
from aiogram.exceptions import TelegramBadRequest

from app.states.profile_states import ProfileState
from app.db.queries import create_or_update_user_profile
from app.keyboards.onboarding import get_profile_preview_keyboard
from app.config import get_settings

router = Router()

# Get settings
settings = get_settings()

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_industry_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with industry options from database"""
    # Get industries from database
    result = supabase.table("industries").select("id, name").execute()
    industries = result.data
    
    builder = InlineKeyboardBuilder()
    
    for industry in industries:
        builder.add(
            InlineKeyboardButton(
                text=industry["name"],
                callback_data=f"industry:{industry['id']}"
            )
        )
    
    # Arrange buttons in 2 columns
    builder.adjust(2)
    return builder.as_markup()

def get_tags_keyboard(industry_id: int) -> InlineKeyboardMarkup:
    """Create keyboard with tag options for selected industry"""
    # Get tags for selected industry
    result = supabase.table("industry_tags") \
        .select("tags(id, name)") \
        .eq("industry_id", industry_id) \
        .execute()
    
    tags = [item["tags"] for item in result.data]
    
    builder = InlineKeyboardBuilder()
    
    for tag in tags:
        builder.add(
            InlineKeyboardButton(
                text=tag["name"],
                callback_data=f"tag:{tag['id']}"
            )
        )
    
    # Add confirm button
    builder.add(
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data="tags_done"
        )
    )
    
    # Arrange buttons in 3 columns
    builder.adjust(3)
    return builder.as_markup()

def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for profile editing options"""
    builder = InlineKeyboardBuilder()
    
    # Add edit buttons
    builder.add(
        InlineKeyboardButton(
            text="👤 Имя",
            callback_data="edit_first_name"
        ),
        InlineKeyboardButton(
            text="👤 Фамилия",
            callback_data="edit_last_name"
        ),
        InlineKeyboardButton(
            text="🏢 Компания",
            callback_data="edit_company"
        ),
        InlineKeyboardButton(
            text="💼 Должность",
            callback_data="edit_title"
        ),
        InlineKeyboardButton(
            text="🏭 Индустрия",
            callback_data="edit_industry"
        ),
        InlineKeyboardButton(
            text="🏷️ Теги",
            callback_data="edit_tags"
        )
    )
    
    # Add back button
    builder.add(
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_preview"
        )
    )
    
    # Arrange buttons in 2 columns
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()

# Start handlers
@router.message(Command("start"))
@router.callback_query(F.data == "create_profile")
async def start_profile_creation(event: Message | CallbackQuery, state: FSMContext):
    """Start profile creation process
    
    Args:
        event: Message or CallbackQuery event
        state: FSM context
    """
    # Clear any existing state
    await state.clear()
    
    # Set initial state
    await state.set_state(ProfileState.waiting_for_first_name)
    
    # Send first question
    text = (
        "👤 Давай создадим твой профиль!\n\n"
        "Как тебя зовут? (Имя)"
    )
    
    if isinstance(event, CallbackQuery):
        await event.message.answer(text)
        await event.answer()
    else:
        await event.answer(text)

# First name handler
@router.message(ProfileState.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    """Process user's first name"""
    # Save first name
    await state.update_data(first_name=message.text)
    
    # Get current state
    current_state = await state.get_state()
    
    # Check if we're in editing mode
    data = await state.get_data()
    is_editing = data.get("editing_mode", False)
    
    if not is_editing:
        # If this is initial profile creation, move to last name
        await state.set_state(ProfileState.waiting_for_last_name)
        await message.answer("👤 Отлично! А как твоя фамилия?")
    else:
        # If this is editing, return to preview
        # Get tag names
        tag_ids = data.get("own_tags", [])
        if tag_ids:
            result = supabase.table("tags") \
                .select("name") \
                .in_("id", tag_ids) \
                .execute()
            tag_names = [tag["name"] for tag in result.data]
        else:
            tag_names = []
        
        # Create preview message
        preview_text = (
            "📝 Проверь свой профиль:\n\n"
            f"👤 Имя: {data['first_name']} {data['last_name']}\n"
            f"🏢 Компания: {data['company']}\n"
            f"💼 Должность: {data['title']}\n"
            f"🏭 Индустрия: {data['industry']}\n"
            f"🏷️ Теги: {', '.join(tag_names)}\n\n"
            "Все верно?"
        )
        
        # Send preview with confirmation keyboard
        await message.answer(
            text=preview_text,
            reply_markup=get_profile_preview_keyboard()
        )
        # Reset editing mode
        await state.update_data(editing_mode=False)
        await state.set_state(ProfileState.waiting_for_confirmation)

# Last name handler
@router.message(ProfileState.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    """Process user's last name"""
    # Save last name
    await state.update_data(last_name=message.text)
    
    # Get current state
    current_state = await state.get_state()
    
    # Check if we're in editing mode
    data = await state.get_data()
    is_editing = data.get("editing_mode", False)
    
    if not is_editing:
        # If this is initial profile creation, move to company
        await state.set_state(ProfileState.waiting_for_company)
        await message.answer("🏢 В какой компании ты работаешь?")
    else:
        # If this is editing, return to preview
        # Get tag names
        tag_ids = data.get("own_tags", [])
        if tag_ids:
            result = supabase.table("tags") \
                .select("name") \
                .in_("id", tag_ids) \
                .execute()
            tag_names = [tag["name"] for tag in result.data]
        else:
            tag_names = []
        
        # Create preview message
        preview_text = (
            "📝 Проверь свой профиль:\n\n"
            f"👤 Имя: {data['first_name']} {data['last_name']}\n"
            f"🏢 Компания: {data['company']}\n"
            f"💼 Должность: {data['title']}\n"
            f"🏭 Индустрия: {data['industry']}\n"
            f"🏷️ Теги: {', '.join(tag_names)}\n\n"
            "Все верно?"
        )
        
        # Send preview with confirmation keyboard
        await message.answer(
            text=preview_text,
            reply_markup=get_profile_preview_keyboard()
        )
        # Reset editing mode
        await state.update_data(editing_mode=False)
        await state.set_state(ProfileState.waiting_for_confirmation)

# Company handler
@router.message(ProfileState.waiting_for_company)
async def process_company(message: Message, state: FSMContext):
    """Process user's company"""
    # Save company
    await state.update_data(company=message.text)
    
    # Get current state
    current_state = await state.get_state()
    
    # Check if we're in editing mode
    data = await state.get_data()
    is_editing = data.get("editing_mode", False)
    
    if not is_editing:
        # If this is initial profile creation, move to title
        await state.set_state(ProfileState.waiting_for_title)
        await message.answer("💼 Какую должность ты занимаешь?")
    else:
        # If this is editing, return to preview
        # Get tag names
        tag_ids = data.get("own_tags", [])
        if tag_ids:
            result = supabase.table("tags") \
                .select("name") \
                .in_("id", tag_ids) \
                .execute()
            tag_names = [tag["name"] for tag in result.data]
        else:
            tag_names = []
        
        # Create preview message
        preview_text = (
            "📝 Проверь свой профиль:\n\n"
            f"👤 Имя: {data['first_name']} {data['last_name']}\n"
            f"🏢 Компания: {data['company']}\n"
            f"💼 Должность: {data['title']}\n"
            f"🏭 Индустрия: {data['industry']}\n"
            f"🏷️ Теги: {', '.join(tag_names)}\n\n"
            "Все верно?"
        )
        
        # Send preview with confirmation keyboard
        await message.answer(
            text=preview_text,
            reply_markup=get_profile_preview_keyboard()
        )
        # Reset editing mode
        await state.update_data(editing_mode=False)
        await state.set_state(ProfileState.waiting_for_confirmation)

# Title handler
@router.message(ProfileState.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Process user's job title"""
    # Save title
    await state.update_data(title=message.text)
    
    # Get current state
    current_state = await state.get_state()
    
    # Check if we're in editing mode
    data = await state.get_data()
    is_editing = data.get("editing_mode", False)
    
    if not is_editing:
        # If this is initial profile creation, move to industry
        await state.set_state(ProfileState.waiting_for_industry)
        await message.answer(
            "🏭 В какой индустрии ты работаешь?",
            reply_markup=get_industry_keyboard()
        )
    else:
        # If this is editing, return to preview
        # Get tag names
        tag_ids = data.get("own_tags", [])
        if tag_ids:
            result = supabase.table("tags") \
                .select("name") \
                .in_("id", tag_ids) \
                .execute()
            tag_names = [tag["name"] for tag in result.data]
        else:
            tag_names = []
        
        # Create preview message
        preview_text = (
            "📝 Проверь свой профиль:\n\n"
            f"👤 Имя: {data['first_name']} {data['last_name']}\n"
            f"🏢 Компания: {data['company']}\n"
            f"💼 Должность: {data['title']}\n"
            f"🏭 Индустрия: {data['industry']}\n"
            f"🏷️ Теги: {', '.join(tag_names)}\n\n"
            "Все верно?"
        )
        
        # Send preview with confirmation keyboard
        await message.answer(
            text=preview_text,
            reply_markup=get_profile_preview_keyboard()
        )
        # Reset editing mode
        await state.update_data(editing_mode=False)
        await state.set_state(ProfileState.waiting_for_confirmation)

# Industry handler
@router.callback_query(ProfileState.waiting_for_industry)
async def process_industry(callback: CallbackQuery, state: FSMContext):
    """Process user's industry selection"""
    if callback.data.startswith("industry:"):
        industry_id = int(callback.data.split(":", 1)[1])
        
        # Get industry name
        result = supabase.table("industries") \
            .select("name") \
            .eq("id", industry_id) \
            .single() \
            .execute()
        
        industry_name = result.data["name"]
        
        # Save industry data
        await state.update_data(industry_id=industry_id, industry=industry_name)
        
        # Get current state
        current_state = await state.get_state()
        
        # Check if we're in editing mode
        data = await state.get_data()
        is_editing = data.get("editing_mode", False)
        
        if not is_editing:
            # If this is initial profile creation, move to tags
            await state.set_state(ProfileState.waiting_for_own_tags)
            
            # Initialize empty tags list
            await state.update_data(own_tags=[])
            
            # Ask for tags with keyboard
            await callback.message.edit_text(
                "🏷️ Выбери до 3 тегов, которые описывают тебя\n"
                "Нажми 'Готово', когда закончишь",
                reply_markup=get_tags_keyboard(industry_id)
            )
        else:
            # If this is editing, move to tags selection
            await state.set_state(ProfileState.waiting_for_own_tags)
            
            # Clear existing tags since industry changed
            await state.update_data(own_tags=[])
            
            # Ask for tags with keyboard
            await callback.message.edit_text(
                "🏷️ Выбери до 3 тегов, которые описывают тебя\n"
                "Нажми 'Готово', когда закончишь",
                reply_markup=get_tags_keyboard(industry_id)
            )
    
    await callback.answer()

# Tags handler
@router.callback_query(ProfileState.waiting_for_own_tags)
async def process_tags(callback: CallbackQuery, state: FSMContext):
    """Process user's tag selection"""
    if callback.data == "tags_done":
        # Get current data
        data = await state.get_data()
        
        # Get tag names
        tag_ids = data.get("own_tags", [])
        if tag_ids:
            result = supabase.table("tags") \
                .select("name") \
                .in_("id", tag_ids) \
                .execute()
            tag_names = [tag["name"] for tag in result.data]
        else:
            tag_names = []
        
        # Create preview message
        preview_text = (
            "📝 Проверь свой профиль:\n\n"
            f"👤 Имя: {data['first_name']} {data['last_name']}\n"
            f"🏢 Компания: {data['company']}\n"
            f"💼 Должность: {data['title']}\n"
            f"🏭 Индустрия: {data['industry']}\n"
            f"🏷️ Теги: {', '.join(tag_names)}\n\n"
            "Все верно?"
        )
        
        # Send preview with confirmation keyboard
        await callback.message.edit_text(
            text=preview_text,
            reply_markup=get_profile_preview_keyboard()
        )
        # Reset editing mode
        await state.update_data(editing_mode=False)
        await state.set_state(ProfileState.waiting_for_confirmation)
        return
    
    if callback.data.startswith("tag:"):
        tag_id = int(callback.data.split(":", 1)[1])
        
        # Get current tags
        data = await state.get_data()
        current_tags = data.get("own_tags", [])
        
        # Toggle tag selection
        if tag_id in current_tags:
            current_tags.remove(tag_id)
        else:
            if len(current_tags) >= 3:
                await callback.answer("Можно выбрать максимум 3 тега", show_alert=True)
                return
            current_tags.append(tag_id)
        
        # Update state
        await state.update_data(own_tags=current_tags)
        
        # Get industry ID
        industry_id = data.get("industry_id")
        
        # Get updated keyboard
        keyboard = get_tags_keyboard(industry_id)
        
        # Update message with new keyboard
        try:
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
            # If the message wasn't modified, just ignore the error
        
        # Show selection status
        if tag_id in current_tags:
            await callback.answer("Тег добавлен")
        else:
            await callback.answer("Тег удален")
    
    await callback.answer()

# Confirmation handler
@router.callback_query(ProfileState.waiting_for_confirmation)
async def process_confirmation(callback: CallbackQuery, state: FSMContext):
    """Process profile confirmation"""
    if callback.data == "confirm_profile":
        # Get all data
        data = await state.get_data()
        
        try:
            # Create or update profile using Supabase
            profile_data = {
                "telegram_id": callback.from_user.id,
                "username": callback.from_user.username,
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "company": data["company"],
                "title": data["title"],
                "industry_id": data["industry_id"]
            }
            
            # Upsert user profile by telegram_id
            result = supabase.table("users") \
                .upsert(profile_data, on_conflict="telegram_id") \
                .execute()
            
            user = result.data[0]
            
            # Handle tags
            if data["own_tags"]:
                # First, delete existing tags for this user
                supabase.table("user_tags") \
                    .delete() \
                    .eq("user_id", user["id"]) \
                    .execute()
                
                # Then create new user-tag associations
                for tag_id in data["own_tags"]:
                    supabase.table("user_tags").insert({
                        "user_id": user["id"],
                        "tag_id": tag_id,
                        "tag_type": "own"
                    }).execute()
            
            # Clear state
            await state.clear()
            
            # Send success message
            await callback.message.edit_text(
                "✅ Профиль успешно создан!\n\n"
                "Теперь ты можешь использовать команду /search для поиска других участников."
            )
            
        except Exception as e:
            # Handle error
            await callback.message.edit_text(
                "❌ Произошла ошибка при создании профиля. Пожалуйста, попробуй позже."
            )
            print(f"Error creating profile: {e}")
            
    elif callback.data == "edit_profile":
        # Move to edit state
        await state.set_state(ProfileState.waiting_for_edit_field)
        
        # Send edit options
        await callback.message.edit_text(
            "Что ты хочешь изменить?",
            reply_markup=get_edit_profile_keyboard()
        )
    
    await callback.answer()

# Edit field handler
@router.callback_query(ProfileState.waiting_for_edit_field)
async def process_edit_field(callback: CallbackQuery, state: FSMContext):
    """Process field selection for editing"""
    if callback.data == "back_to_preview":
        # Get current data
        data = await state.get_data()
        
        # Get tag names
        tag_ids = data.get("own_tags", [])
        if tag_ids:
            result = supabase.table("tags") \
                .select("name") \
                .in_("id", tag_ids) \
                .execute()
            tag_names = [tag["name"] for tag in result.data]
        else:
            tag_names = []
        
        # Create preview message
        preview_text = (
            "📝 Проверь свой профиль:\n\n"
            f"👤 Имя: {data['first_name']} {data['last_name']}\n"
            f"🏢 Компания: {data['company']}\n"
            f"💼 Должность: {data['title']}\n"
            f"🏭 Индустрия: {data['industry']}\n"
            f"🏷️ Теги: {', '.join(tag_names)}\n\n"
            "Все верно?"
        )
        
        # Send preview with confirmation keyboard
        await callback.message.edit_text(
            text=preview_text,
            reply_markup=get_profile_preview_keyboard()
        )
        await state.set_state(ProfileState.waiting_for_confirmation)
        return
    
    # Get current data
    data = await state.get_data()
    
    # Set editing mode flag
    await state.update_data(editing_mode=True)
    
    # Map callback data to states and handlers
    edit_map = {
        "edit_first_name": {
            "state": ProfileState.waiting_for_first_name,
            "question": f"Как тебя зовут? (Имя)\nТекущее значение: {data['first_name']}",
            "handler": process_first_name
        },
        "edit_last_name": {
            "state": ProfileState.waiting_for_last_name,
            "question": f"Как твоя фамилия?\nТекущее значение: {data['last_name']}",
            "handler": process_last_name
        },
        "edit_company": {
            "state": ProfileState.waiting_for_company,
            "question": f"В какой компании ты работаешь?\nТекущее значение: {data['company']}",
            "handler": process_company
        },
        "edit_title": {
            "state": ProfileState.waiting_for_title,
            "question": f"Какую должность ты занимаешь?\nТекущее значение: {data['title']}",
            "handler": process_title
        },
        "edit_industry": {
            "state": ProfileState.waiting_for_industry,
            "question": f"В какой индустрии ты работаешь?\nТекущее значение: {data['industry']}",
            "handler": process_industry
        },
        "edit_tags": {
            "state": ProfileState.waiting_for_own_tags,
            "question": "Выбери до 3 тегов, которые описывают тебя",
            "handler": process_tags
        }
    }
    
    # Get edit info
    edit_info = edit_map.get(callback.data)
    if edit_info:
        # Set new state
        await state.set_state(edit_info["state"])
        
        # Send appropriate question
        if callback.data == "edit_industry":
            await callback.message.edit_text(
                edit_info["question"],
                reply_markup=get_industry_keyboard()
            )
        elif callback.data == "edit_tags":
            # Get current industry
            industry_id = data.get("industry_id")
            if not industry_id:
                # If no industry selected, force industry selection first
                await callback.message.edit_text(
                    "Сначала выбери индустрию, а затем теги",
                    reply_markup=get_industry_keyboard()
                )
                await state.set_state(ProfileState.waiting_for_industry)
            else:
                # Keep existing tags
                await callback.message.edit_text(
                    edit_info["question"],
                    reply_markup=get_tags_keyboard(industry_id)
                )
        else:
            await callback.message.edit_text(edit_info["question"])
    
    await callback.answer() 