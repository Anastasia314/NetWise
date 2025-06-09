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

# Create router
router = Router()

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
    waiting_for_search_query = State()

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
        f"🏷 Теги: {tags_str}"
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
    
    # Create keyboard for search type selection
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔍 Поиск по своим тегам",
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
    current_user = user_result.data
    
    # Get selected tags
    selected_tags = await state.get_data()
    selected_tags = selected_tags.get("search_tags", [])
    
    if callback.data.startswith("industry:"):
        industry_id = int(callback.data.split(":")[1])
        
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
                callback_data="confirm_search_tags"
            )
        )
        
        builder.adjust(3)
        
        # Show selected tags
        selected_tag_names = []
        if selected_tags:
            tag_result = supabase.table("tags") \
                .select("name") \
                .in_("id", selected_tags) \
                .execute()
            selected_tag_names = [tag["name"] for tag in tag_result.data]
        
        await callback.message.edit_text(
            f"Выберите теги для поиска (до 3):\n",
            reply_markup=builder.as_markup()
        )
        
    elif callback.data.startswith("tag:"):
        tag_id = int(callback.data.split(":")[1])
        
        if tag_id in selected_tags:
            selected_tags.remove(tag_id)
        else:
            if len(selected_tags) >= 3:
                await callback.answer("❌ Можно выбрать не более 3 тегов")
                return
            selected_tags.append(tag_id)
        
        await state.update_data(search_tags=selected_tags)
        
        # Get tag names for display
        tag_result = supabase.table("tags") \
            .select("name") \
            .in_("id", selected_tags) \
            .execute()
        selected_tag_names = [tag["name"] for tag in tag_result.data]
        
        # Show selection status
        if tag_id in selected_tags:
            await callback.answer("Тег добавлен")
        else:
            await callback.answer("Тег удален")
            
    elif callback.data == "confirm_search_tags":
        if not selected_tags:
            await callback.answer("❌ Выберите хотя бы один тег")
            return
            
        # Get tag names for display
        result = supabase.table("tags") \
            .select("name") \
            .in_("id", selected_tags) \
            .execute()
        tag_names = [tag["name"] for tag in result.data]
        
        # Save search tags and their IDs
        await state.update_data(
            search_tags=tag_names,
            tag_ids=selected_tags,
            current_page=1
        )
        
        # Find matching users
        matching_users, total_count = find_matching_users(
            supabase, 
            current_user, 
            RESULTS_PER_PAGE, 
            0,
            selected_tags
        )
        
        if not matching_users:
            await callback.message.edit_text(
                f"😔 Не найдено пользователей, соответствующих выбранным тегам:\n"
                f"🏷 {', '.join(tag_names)}\n\n"
                f"Новый поиск /search"
            )
            return
        
        # Calculate total pages
        total_pages = (total_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        
        # Format results
        results_text = "🔍 Результаты поиска:\n\n"
        for user in matching_users:
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

@router.callback_query(F.data.startswith("pagination:"))
async def pagination_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle pagination callback"""
    try:
        logger.info("="*50)
        logger.info("PAGINATION CALLBACK RECEIVED")
        logger.info(f"Callback data: {callback_query.data}")
        
        # Get requested page number
        requested_page = int(callback_query.data.split(":")[1])
        logger.info(f"Requested page: {requested_page}")
        
        # Get current state
        state_data = await state.get_data()
        current_page = state_data.get("current_page", 1)
        search_tags = state_data.get("search_tags", [])
        
        logger.info(f"Current page from state: {current_page}")
        logger.info(f"Search tags from state: {search_tags}")
        
        # Check if user exists
        user = get_user_profile(callback_query.bot.get("supabase"), callback_query.from_user.id)
        if not user:
            logger.warning(f"User not found: {callback_query.from_user.id}")
            await callback_query.answer("Пожалуйста, сначала заполните свой профиль")
            return
            
        # Calculate offset
        limit = 5  # Fixed limit per page
        offset = (requested_page - 1) * limit
        logger.info(f"Pagination params: limit={limit}, offset={offset}")
        
        # Get matching users with pagination
        matching_users, total_count = find_matching_users(
            callback_query.bot.get("supabase"),
            user,
            limit=limit,
            offset=offset,
            selected_tags=search_tags
        )
        
        logger.info(f"Found {len(matching_users)} users, total count: {total_count}")
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit
        logger.info(f"Total pages: {total_pages}")
        
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
            logger.info(f"Created keyboard for page {requested_page}")
            logger.info(f"Keyboard buttons: {[btn.callback_data for btn in keyboard.inline_keyboard[0]]}")
            
            await callback_query.message.edit_text(
                results_text,
                reply_markup=keyboard
            )
            # Update current page in state
            await state.update_data(current_page=requested_page)
            await callback_query.answer()
            logger.info(f"Successfully updated message for page {requested_page}")
            
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
        logger.error(f"Error in pagination callback: {e}")
        logger.exception("Full traceback:")
        await callback_query.answer("Произошла ошибка при обработке запроса")
    finally:
        logger.info("PAGINATION CALLBACK HANDLING ENDED")
        logger.info("="*50)

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

@router.message(StateFilter(SearchState.waiting_for_search_query))
async def process_search_query(message: Message, state: FSMContext):
    """Process free search query
    
    Args:
        message: Message object
        state: FSM context
    """
    query = message.text.strip()
    
    # Get current user
    current_user = supabase.table("users") \
        .select("*") \
        .eq("telegram_id", message.from_user.id) \
        .single() \
        .execute()
    
    if not current_user.data:
        await message.answer("❌ Сначала создайте свой профиль!")
        return
        
    # Search for tags matching the query
    result = supabase.table("tags") \
        .select("id, name") \
        .ilike("name", f"%{query}%") \
        .execute()
        
    if not result.data:
        await message.answer(
            f"😔 Не найдено тегов, соответствующих запросу: {query}\n\n"
            f"Новый поиск /search"
        )
        return
        
    # Get tag IDs
    tag_ids = [tag["id"] for tag in result.data]
    tag_names = [tag["name"] for tag in result.data]
    
    # Save search tags and their IDs
    await state.update_data(
        search_tags=tag_names,
        tag_ids=tag_ids
    )
    
    # Find matching users
    matching_users, total_count = find_matching_users(
        supabase, 
        current_user.data, 
        RESULTS_PER_PAGE, 
        0,
        tag_ids
    )
    
    if not matching_users:
        await message.answer(
            f"😔 Не найдено пользователей, соответствующих тегам:\n"
            f"🏷 {', '.join(tag_names)}\n\n"
            f"Новый поиск /search"
        )
        return
        
    # Calculate total pages
    total_pages = (total_count + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
    
    # Format results
    results_text = "🔍 Результаты поиска:\n\n"
    for user in matching_users:
        results_text += format_user_card(user) + "\n\n"
        
    # Add pagination info
    results_text += f"\nСтраница 1 из {total_pages}\n"
    results_text += "Новый поиск /search"
    
    # Create pagination keyboard
    keyboard = get_pagination_keyboard(1, total_pages)
    
    # Send results
    await message.answer(
        results_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # Save current page in state
    await state.update_data(current_page=1)

@router.callback_query(F.data.startswith("tag_"))
async def process_search_tags(callback: CallbackQuery, state: FSMContext):
    """Process tag selection for search
    
    Args:
        callback: CallbackQuery object
        state: FSM context
    """
    # Get tag ID from callback data
    tag_id = int(callback.data.split("_")[1])
    
    # Get current selected tags from state
    state_data = await state.get_data()
    selected_tags = state_data.get("selected_tags", [])
    
    # Toggle tag selection
    if tag_id in selected_tags:
        selected_tags.remove(tag_id)
    else:
        selected_tags.append(tag_id)
    
    # Update state
    await state.update_data(selected_tags=selected_tags)
    
    # Get tag names for display
    result = supabase.table("tags") \
        .select("name") \
        .in_("id", selected_tags) \
        .execute()
    tag_names = [tag["name"] for tag in result.data]
    
    # Update message with selected tags
    await callback.message.edit_text(
        f"Выбранные теги: {', '.join(tag_names) if tag_names else 'Нет'}\n\n"
        f"Выберите теги для поиска или нажмите 'Готово'",
        reply_markup=get_tags_keyboard(selected_tags)
    )
    
    await callback.answer() 