from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from .models import User, Tag, user_tag

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