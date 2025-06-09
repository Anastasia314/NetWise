from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from supabase import create_client, Client
from typing import List
from app.config import get_settings
from aiogram.exceptions import TelegramBadRequest
import logging

from app.db.queries import find_matching_users, get_user_profile
from app.keyboards.inline import get_contact_card_keyboard, get_pagination_keyboard
from app.keyboards.onboarding import get_industry_keyboard, get_tags_keyboard

# Configure logger
logger = logging.getLogger(__name__)

# Create routers
router = Router()
pagination_router = Router()

# Get settings
settings = get_settings()

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Number of results per page
RESULTS_PER_PAGE = 5

class SearchState(StatesGroup):
    """Search states"""
    waiting_for_search_type = State()
    waiting_for_search_tags = State()
    waiting_for_tag_selection = State()  # New state for tag selection

def format_user_card(user_data: dict) -> str:
    """
    Format user data into a card-like string representation.
    
    Args:
        user_data: Dictionary containing user profile data
        
    Returns:
        Formatted string with user information
    """
    # Get user details with defaults
    first_name = user_data.get("first_name", "")
    last_name = user_data.get("last_name", "")
    company = user_data.get("company", "Не указано")
    title = user_data.get("title", "Не указано")
    username = user_data.get("username", "")
    
    # Get industry name from nested dictionary
    industry = user_data.get("industries", {}).get("name", "Не указано")
    
    # Get tags from user_tags list
    tags = [tag.get("tags", {}).get("name", "") for tag in user_data.get("user_tags", [])]
    tags_str = ", ".join(tags) if tags else "Не указано"
    
    # Format full name
    full_name = f"{first_name} {last_name}".strip() or "Не указано"
    
    # Format the card
    card = (
        f"👤 {full_name}\n"
        f"🏢 Компания: {company}\n"
        f"💼 Должность: {title}\n"
        f"🏭 Отрасль: {industry}\n"
        f"🏷 Теги: {tags_str}\n"
        f"✍️ Написать: @{username}" if username else "✍️ Написать: не указан"
    )
    
    return card

@router.message(Command("search"))
async def search_command(message: Message, state: FSMContext):
    """Handle /search command"""
    # Get current user
    user_result = supabase.table("users").select("*").eq("telegram_id", message.from_user.id).single().execute()
    if not user_result.data:
        await message.answer("❌ Сначала создайте свой профиль!")
        return
    
    # Get user's tags
    user_tags_result = supabase.table("user_tags") \
        .select("tags(name)") \
        .eq("user_id", user_result.data["id"]) \
        .execute()
    
    user_tags = [tag["tags"]["name"] for tag in user_tags_result.data]
    tags_str = ", ".join(user_tags) if user_tags else "Нет тегов"
    
    # Create keyboard for search type selection
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"🔍 Поиск по своим тегам ({tags_str})",
            callback_data="search_by_own_tags"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔎 Свободный поиск",
            callback_data="search_by_other_tags"
        )
    )
    
    # Ask for search type
    await message.answer(
        "Выберите тип поиска:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(SearchState.waiting_for_search_type)

@router.callback_query(SearchState.waiting_for_search_type)
async def process_search_type(callback: CallbackQuery, state: FSMContext):
    """Process search type selection"""
    if callback.data == "search_by_own_tags":
        # Get current user
        user_result = supabase.table("users") \
            .select("*, industries!inner(*), user_tags(tags(name))") \
            .eq("telegram_id", callback.from_user.id) \
            .single() \
            .execute()
        current_user = user_result.data
        
        # Get user's tags
        user_tags = [tag["tags"]["name"] for tag in current_user.get("user_tags", [])]
        
        # Save search type and tags
        await state.update_data(
            search_type="own_tags",
            search_tags=user_tags
        )
        
        # Find matching users
        matching_users, total_count = find_matching_users(supabase, current_user, RESULTS_PER_PAGE, 0)
        
        if not matching_users:
            await callback.message.edit_text(
                f"😔 Не найдено пользователей, соответствующих вашим тегам:\n"
                f"🏷 {', '.join(user_tags) if user_tags else 'Нет тегов'}\n\n"
                f"Новый поиск /search"
            )
            return
        
        # Format results
        total_pages = (total_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        
        # Create message with results
        message_text = [
            f"🔍 Результаты поиска по вашим тегам:",
            f"🏷 {', '.join(user_tags) if user_tags else 'Нет тегов'}",
            f"\nСтраница 1/{total_pages}:",
            ""
        ]
        
        # Add each user card
        for user in matching_users:
            message_text.extend([
                "➖➖➖➖➖➖➖➖➖➖",
                format_user_card(user),
                ""
            ])
        
        # Add new search message
        message_text.append("\nНовый поиск /search")
        
        # Create keyboard with pagination
        keyboard = get_pagination_keyboard(1, total_pages)
        
        # Send results with pagination
        await callback.message.edit_text(
            "\n".join(message_text),
            reply_markup=keyboard
        )
        
    elif callback.data == "search_by_other_tags":
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
        builder.adjust(2)
        
        # Save search type
        await state.update_data(search_type="other_tags")
        
        # Show industry selection
        await callback.message.edit_text(
            "Выберите индустрию для поиска тегов:\n\n"
            "Новый поиск /search",
            reply_markup=builder.as_markup()
        )
        await state.set_state(SearchState.waiting_for_search_tags)
    
    await callback.answer()

@router.callback_query(SearchState.waiting_for_search_tags)
async def process_search_tags(callback: CallbackQuery, state: FSMContext):
    """Process search tags selection"""
    # Get current user
    user_result = supabase.table("users") \
        .select("*, industries!inner(*)") \
        .eq("telegram_id", callback.from_user.id) \
        .single() \
        .execute()
    
    if not user_result.data:
        await callback.answer("❌ Сначала создайте свой профиль!")
        return
    
    # Get industry ID from callback data
    industry_id = int(callback.data.split(":")[1])
    
    # Get tags for selected industry
    result = supabase.table("industry_tags") \
        .select("tags(id, name)") \
        .eq("industry_id", industry_id) \
        .execute()
    
    if not result.data:
        await callback.answer("❌ Не найдено тегов для выбранной индустрии")
        return
    
    # Get tag IDs
    tag_ids = [tag["tags"]["id"] for tag in result.data]
    
    # Save industry ID and initialize selected tags
    await state.update_data(
        industry_id=industry_id,
        selected_tags=[]  # Initialize empty list for selected tags
    )
    
    # Create keyboard with tags
    keyboard = get_search_tags_keyboard(tag_ids)
    
    # Show tag selection
    await callback.message.edit_text(
        "🔍 Выберите от 1 до 3 тегов для поиска:\n"
        "Нажмите на теги, которые хотите использовать для поиска.\n"
        "После выбора нажмите 'Готово'.",
        reply_markup=keyboard
    )
    await state.set_state(SearchState.waiting_for_tag_selection)
    
    await callback.answer()

@pagination_router.callback_query(F.data.startswith("pagination:"))
async def pagination_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle pagination callback"""
    try:

        # Get requested page number
        requested_page = int(callback_query.data.split(":")[1])
        
        # Get current state
        state_data = await state.get_data()
        current_page = state_data.get("current_page", 1)
        selected_tags = state_data.get("selected_tags", [])
        
        # Check if user exists
        user = get_user_profile(supabase, callback_query.from_user.id)
        if not user:
            logger.warning(f"User not found: {callback_query.from_user.id}")
            await callback_query.answer("Пожалуйста, сначала заполните свой профиль")
            return
            
        # Calculate offset
        limit = RESULTS_PER_PAGE
        offset = (requested_page - 1) * limit
        logger.info(f"Pagination params: limit={limit}, offset={offset}")
        
        # Get matching users with pagination
        matching_users, total_count = find_matching_users(
            supabase,
            user,
            limit=limit,
            offset=offset,
            selected_tags=selected_tags
        )

        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit
        
        if not matching_users:
            await callback_query.answer("Больше пользователей не найдено")
            return
        
        # Format results
        results_text = "Найдены следующие пользователи:\n\n"
        for user_data in matching_users:
            results_text += format_user_card(user_data) + "\n\n"
            
        # Add pagination info
        results_text += f"\nСтраница {requested_page} из {total_pages}"
        results_text += "\n\nНажмите /search чтобы начать новый поиск"
        
        # Update message with new results and keyboard
        try:
            keyboard = get_pagination_keyboard(requested_page, total_pages)
            
            await callback_query.message.edit_text(
                results_text,
                reply_markup=keyboard
            )
            # Update current page in state
            await state.update_data(current_page=requested_page)
            await callback_query.answer()
            
        except TelegramBadRequest as e:
            logger.error(f"TelegramBadRequest error: {str(e)}")
            if "message is not modified" in str(e):
                await callback_query.answer()
            elif "query is too old" in str(e):
                await callback_query.answer("Время ожидания истекло. Пожалуйста, начните поиск заново")
            else:
                logger.error(f"Error updating message: {e}")
                await callback_query.answer("Произошла ошибка при обновлении результатов")
                
    except Exception as e:
        await callback_query.answer("Произошла ошибка при обработке запроса")
    finally:
        logger.info("PAGINATION CALLBACK HANDLING ENDED")

@router.callback_query(F.data.startswith("contact_"))
async def contact_user(callback: CallbackQuery):
    """Handle contact button click
    
    Args:
        callback: CallbackQuery object
    """
    # Get user ID from callback data
    user_id = int(callback.data.split("_")[1])
    
    # Get user data
    user_result = supabase.table("users") \
        .select("*, industries!inner(*)") \
        .eq("id", user_id) \
        .single() \
        .execute()
    
    if not user_result.data:
        await callback.answer("❌ Пользователь не найден")
        return
    
    user = user_result.data
    
    # Create contact message
    contact_text = (
        f"👤 {user['first_name']} {user['last_name']}\n"
        f"🏢 {user['company']}\n"
        f"💼 {user['title']}\n"
        f"🏭 {user['industry']['name'] if isinstance(user['industry'], dict) else user['industry']}\n\n"
        "Нажмите на имя пользователя, чтобы начать чат."
    )
    
    # Send contact info
    await callback.message.answer(contact_text)
    await callback.answer()

def get_search_tags_keyboard(tag_ids: list[int], selected_tags: list[int] = None) -> InlineKeyboardMarkup:
    """Create keyboard with tag options for search
    
    Args:
        tag_ids: List of tag IDs to show
        selected_tags: List of currently selected tag IDs
        
    Returns:
        InlineKeyboardMarkup with tag buttons and confirm button
    """
    if selected_tags is None:
        selected_tags = []
        
    # Get tag names
    result = supabase.table("tags") \
        .select("id, name") \
        .in_("id", tag_ids) \
        .execute()
    
    builder = InlineKeyboardBuilder()
    
    # Add tag buttons
    for tag in result.data:
        builder.add(
            InlineKeyboardButton(
                text=f"{'✅ ' if tag['id'] in selected_tags else ''}{tag['name']}",
                callback_data=f"search_tag_{tag['id']}"
            )
        )
    
    # Add confirm button
    builder.add(
        InlineKeyboardButton(
            text="✅ Готово",
            callback_data="search_done"
        )
    )
    
    # Calculate number of rows needed for tags (3 buttons per row)
    num_tag_rows = (len(result.data) + 2) // 3  # Round up division
    
    # Adjust layout - 3 buttons per row for tags, Done button on new row
    builder.adjust(3, repeat=num_tag_rows)  # 3 buttons per row for all tag rows
    
    return builder.as_markup()

@router.callback_query(SearchState.waiting_for_tag_selection, F.data.startswith("search_tag_"))
async def process_search_tag_selection(callback: CallbackQuery, state: FSMContext):
    """Process tag selection in free search"""
    # Get tag ID from callback data
    tag_id = int(callback.data.split("_")[2])
    
    # Get current state
    state_data = await state.get_data()
    selected_tags = state_data.get("selected_tags", [])
    tag_ids = state_data.get("tag_ids", [])
    
    # Check if we already have 3 tags selected
    if len(selected_tags) >= 3 and tag_id not in selected_tags:
        await callback.answer("❌ Можно выбрать максимум 3 тега")
        return
    
    # Toggle tag selection
    if tag_id in selected_tags:
        selected_tags.remove(tag_id)
    else:
        selected_tags.append(tag_id)

@router.callback_query(SearchState.waiting_for_tag_selection, F.data == "search_done")
async def process_search_done(callback: CallbackQuery, state: FSMContext):
    """Process search completion"""
    # Get selected tags
    state_data = await state.get_data()
    selected_tags = state_data.get("selected_tags", [])
    
    if not selected_tags:
        await callback.answer("❌ Выберите хотя бы один тег")
        return
    
    if len(selected_tags) > 3:
        await callback.answer("❌ Можно выбрать максимум 3 тега")
        return
    
    # Get current user
    current_user = supabase.table("users") \
        .select("*") \
        .eq("telegram_id", callback.from_user.id) \
        .single() \
        .execute()
    
    if not current_user.data:
        await callback.answer("❌ Сначала создайте свой профиль!")
        return
    
    # Find matching users
    matching_users, total_count = find_matching_users(
        supabase, 
        current_user.data, 
        RESULTS_PER_PAGE, 
        0,
        selected_tags
    )
    
    if not matching_users:
        # Get tag names for display
        tag_result = supabase.table("tags") \
            .select("name") \
            .in_("id", selected_tags) \
            .execute()
        tag_names = [tag["name"] for tag in tag_result.data]
        
        await callback.message.edit_text(
            f"😔 Не найдено пользователей, соответствующих тегам:\n"
            f"🏷 {', '.join(tag_names)}\n\n"
            f"Новый поиск /search"
        )
        return
    
    # Calculate total pages
    total_pages = (total_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
    
    # Get tag names for display
    tag_result = supabase.table("tags") \
        .select("name") \
        .in_("id", selected_tags) \
        .execute()
    tag_names = [tag["name"] for tag in tag_result.data]
    
    # Format results
    results_text = f"🔍 Результаты поиска по тегам:\n🏷 {', '.join(tag_names)}\n\n"
    
    # Add each user card with separator
    for user in matching_users:
        results_text += "➖➖➖➖➖➖➖➖➖➖\n"
        results_text += format_user_card(user) + "\n\n"
        
    # Add pagination info
    results_text += f"\nСтраница 1 из {total_pages}\n"
    results_text += "Новый поиск /search"
    
    # Create pagination keyboard
    keyboard = get_pagination_keyboard(1, total_pages)
    
    # Send results
    await callback.message.edit_text(
        results_text,
        reply_markup=keyboard
    )
    
    await callback.answer() 