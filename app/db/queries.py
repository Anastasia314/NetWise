from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict
from datetime import datetime
from .models import User, Tag, user_tag
from supabase import Client

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