from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from app.db.queries import get_all_tags, get_all_industries

def get_onboarding_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for onboarding with profile creation button
    
    Returns:
        InlineKeyboardMarkup: Keyboard with "Create Profile" button
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="🚀 Создать профиль",
            callback_data="create_profile"
        )
    )
    
    return builder.as_markup()

def get_profile_preview_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for profile preview with confirmation buttons
    
    Returns:
        InlineKeyboardMarkup: Keyboard with "Confirm" and "Edit" buttons
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="✅ Все верно",
            callback_data="confirm_profile"
        ),
        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data="edit_profile"
        )
    )
    
    return builder.as_markup()

def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for selecting field to edit
    
    Returns:
        InlineKeyboardMarkup: Keyboard with buttons for each field
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text="👤 Имя",
            callback_data="edit_name"
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
    
    # Arrange buttons in 2 columns
    builder.adjust(2)
    
    return builder.as_markup()

def get_industry_keyboard(db: Session) -> InlineKeyboardMarkup:
    """Create keyboard for industry selection using industries from database
    
    Args:
        db: Database session
        
    Returns:
        InlineKeyboardMarkup: Keyboard with industry options
    """
    builder = InlineKeyboardBuilder()
    
    # Get industries from database
    industries = get_all_industries(db)
    
    for industry in industries:
        builder.add(
            InlineKeyboardButton(
                text=industry,
                callback_data=f"industry_{industry}"
            )
        )
    
    # Arrange buttons in 2 columns
    builder.adjust(2)
    
    return builder.as_markup()

def get_tags_keyboard(db: Session) -> InlineKeyboardMarkup:
    """Create keyboard for tag selection using tags from database
    
    Args:
        db: Database session
        
    Returns:
        InlineKeyboardMarkup: Keyboard with tag options
    """
    builder = InlineKeyboardBuilder()
    
    # Get tags from database
    tags = get_all_tags(db)
    
    for tag in tags:
        builder.add(
            InlineKeyboardButton(
                text=tag,
                callback_data=f"tag_{tag}"
            )
        )
    
    # Arrange buttons in 3 columns
    builder.adjust(3)
    
    return builder.as_markup() 