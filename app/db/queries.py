from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from .models import User, Tag, user_tag
from supabase import Client
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TagType(str):
    OWN = 'own'
    SEARCH = 'search'

def create_or_update_user_profile(
    db: Session,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company: Optional[str] = None,
    title: Optional[str] = None,
    industry: Optional[str] = None,
    own_tags: Optional[List[str]] = None
) -> User:
    """Create or update user profile with tags in a single transaction
    
    Args:
        db: Database session
        telegram_id: User's Telegram ID
        username: User's username
        first_name: User's first name
        last_name: User's last name
        company: User's company
        title: User's job title
        industry: User's industry
        own_tags: List of tags describing the user
        
    Returns:
        User: Created or updated user object
        
    Raises:
        IntegrityError: If there's a database constraint violation
    """
    try:
        # Start transaction
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                company=company,
                title=title,
                industry=industry
            )
            db.add(user)
            db.flush()  # Get user.id without committing
        
        # Update user info
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.company = company
        user.title = title
        user.industry = industry
        user.updated_at = datetime.utcnow()
        
        # Handle own tags if provided
        if own_tags:
            # Remove old own tags
            stmt = user_tag.delete().where(
                user_tag.c.user_id == user.id,
                user_tag.c.tag_type == TagType.OWN
            )
            db.execute(stmt)
            
            # Add new own tags
            for tag_name in own_tags:
                # Find or create tag
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                
                # Create user-tag association
                stmt = user_tag.insert().values(
                    user_id=user.id,
                    tag_id=tag.id,
                    tag_type=TagType.OWN
                )
                db.execute(stmt)
        
        # Create tags from company, title and industry
        if company:
            update_user_company_tags(db, user.id, company)
        if title:
            update_user_title_tags(db, user.id, title)
        if industry:
            update_user_industry_tags(db, user.id, industry)
        
        db.commit()
        return user
        
    except IntegrityError:
        db.rollback()
        raise

def update_user_company_tags(db: Session, user_id: int, company: str) -> None:
    """Update user's company tags"""
    tag = db.query(Tag).filter(Tag.name == company).first()
    if not tag:
        tag = Tag(name=company)
        db.add(tag)
        db.flush()
    
    # Remove old company tag
    stmt = user_tag.delete().where(
        user_tag.c.user_id == user_id,
        user_tag.c.tag_type == TagType.OWN
    )
    db.execute(stmt)
    
    # Add new company tag
    stmt = user_tag.insert().values(
        user_id=user_id,
        tag_id=tag.id,
        tag_type=TagType.OWN
    )
    db.execute(stmt)

def update_user_title_tags(db: Session, user_id: int, title: str) -> None:
    """Update user's title tags"""
    tag = db.query(Tag).filter(Tag.name == title).first()
    if not tag:
        tag = Tag(name=title)
        db.add(tag)
        db.flush()
    
    # Remove old title tag
    stmt = user_tag.delete().where(
        user_tag.c.user_id == user_id,
        user_tag.c.tag_type == TagType.OWN
    )
    db.execute(stmt)
    
    # Add new title tag
    stmt = user_tag.insert().values(
        user_id=user_id,
        tag_id=tag.id,
        tag_type=TagType.OWN
    )
    db.execute(stmt)

def update_user_industry_tags(db: Session, user_id: int, industry: str) -> None:
    """Update user's industry tags"""
    tag = db.query(Tag).filter(Tag.name == industry).first()
    if not tag:
        tag = Tag(name=industry)
        db.add(tag)
        db.flush()
    
    # Remove old industry tag
    stmt = user_tag.delete().where(
        user_tag.c.user_id == user_id,
        user_tag.c.tag_type == TagType.OWN
    )
    db.execute(stmt)
    
    # Add new industry tag
    stmt = user_tag.insert().values(
        user_id=user_id,
        tag_id=tag.id,
        tag_type=TagType.OWN
    )
    db.execute(stmt)

def get_user_profile(supabase: Client, telegram_id: int) -> Optional[Dict]:
    """
    Get full user profile data including tags.
    
    Args:
        supabase: Supabase client instance
        telegram_id: User's Telegram ID
        
    Returns:
        Dict containing user profile data or None if user not found
    """
    try:
        # Get user data with industry
        user_result = supabase.table("users") \
            .select("*, industries(name)") \
            .eq("telegram_id", telegram_id) \
            .eq("is_active", True) \
            .single() \
            .execute()
        
        if not user_result.data:
            return None
            
        user_data = user_result.data
        
        # Get user tags
        tags_result = supabase.table("user_tags") \
            .select("tags(id, name)") \
            .eq("user_id", user_data["id"]) \
            .execute()
            
        # Extract tag names
        user_data["tags"] = [tag["tags"]["name"] for tag in tags_result.data]
        
        return user_data
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

def set_user_inactive(supabase: Client, telegram_id: int) -> bool:
    """
    Soft delete user by setting is_active to false.
    
    Args:
        supabase: Supabase client instance
        telegram_id: User's Telegram ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = supabase.table("users") \
            .update({"is_active": False}) \
            .eq("telegram_id", telegram_id) \
            .execute()
            
        return bool(result.data)
        
    except Exception as e:
        print(f"Error setting user inactive: {e}")
        return False


def get_all_tags(db: Session) -> List[str]:
    """Get all available tags from the database
    
    Args:
        db: Database session
        
    Returns:
        List[str]: List of tag names
    """
    tags = db.query(Tag.name).order_by(Tag.name).all()
    return [tag[0] for tag in tags]

def get_all_industries(db: Session) -> List[str]:
    """Get all available industries from the database
    
    Args:
        db: Database session
        
    Returns:
        List[str]: List of industry names
    """
    # Get unique industries from users table
    industries = db.query(User.industry).distinct().filter(User.industry.isnot(None)).order_by(User.industry).all()
    return [industry[0] for industry in industries]

def find_matching_users(supabase, current_user: dict, limit: int = 5, offset: int = 0, selected_tags: List[int] = None) -> Tuple[List[dict], int]:
    """Find users whose tags match the current user's search tags
    
    Args:
        supabase: Supabase client
        current_user: Current user data
        limit: Number of results per page (fixed)
        offset: Offset for pagination (variable, calculated as (page - 1) * limit)
        selected_tags: List of tag IDs to search by (optional)
        
    Returns:
        Tuple of (list of matching user profiles, total count)
    """
    logger.info(f"Starting find_matching_users with limit={limit}, offset={offset}")
    logger.info(f"Current user ID: {current_user.get('id')}")
    logger.info(f"Selected tags: {selected_tags}")
    
    # Get user's search tags if not provided
    if not selected_tags:
        logger.info("No selected tags provided, fetching user's tags")
        # Get user's tags
        result = supabase.table("user_tags") \
            .select("tag_id") \
            .eq("user_id", current_user["id"]) \
            .execute()
        selected_tags = [tag["tag_id"] for tag in result.data]
        logger.info(f"Fetched user tags: {selected_tags}")
    
    if not selected_tags:
        logger.info("No tags found, returning empty result")
        return [], 0
        
    # First get total count of matching users
    logger.info("Getting total count of matching users")
    count_result = supabase.table("user_tags") \
        .select("user_id", count="exact") \
        .in_("tag_id", selected_tags) \
        .neq("user_id", current_user["id"]) \
        .execute()
    
    total_count = count_result.count if count_result.count is not None else 0
    logger.info(f"Total matching users count: {total_count}")
    
    if total_count == 0:
        logger.info("No matching users found, returning empty result")
        return [], 0
        
    # Get all matching user IDs first
    logger.info("Fetching all matching user IDs")
    result = supabase.table("user_tags") \
        .select("user_id") \
        .in_("tag_id", selected_tags) \
        .neq("user_id", current_user["id"]) \
        .execute()
        
    if not result.data:
        logger.info("No user IDs found in result data")
        return [], total_count
        
    # Get unique user IDs
    all_user_ids = list(set(tag["user_id"] for tag in result.data))
    logger.info(f"Total unique user IDs found: {len(all_user_ids)}")
    logger.info(f"All user IDs: {all_user_ids}")
    
    # Apply pagination to the list of user IDs
    start_idx = offset
    end_idx = min(offset + limit, len(all_user_ids))
    paginated_user_ids = all_user_ids[start_idx:end_idx]
    logger.info(f"Pagination: start_idx={start_idx}, end_idx={end_idx}")
    logger.info(f"Paginated user IDs: {paginated_user_ids}")
    
    if not paginated_user_ids:
        logger.info("No users in paginated result")
        return [], total_count
    
    # Get user profiles with their tags and industry
    logger.info("Fetching user profiles for paginated IDs")
    users_result = supabase.table("users") \
        .select("*, industries!inner(id,name), user_tags!inner(tags!inner(id,name))") \
        .in_("id", paginated_user_ids) \
        .execute()
    
    logger.info(f"Found {len(users_result.data)} user profiles")
    
    # Проверяем, есть ли еще страницы
    has_next_page = end_idx < len(all_user_ids)
    logger.info(f"Has next page: {has_next_page}")
    
    return users_result.data, total_count 