"""
User-related Pydantic models for request/response validation and data serialization.

This module contains models for:
- Basic user information (UserBase)
- User creation/registration (UserCreate)
- Profile updates (UserProfileUpdate)
- Database representation (UserInDBBase)
- API responses (UserResponse)
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common_models import SubscriptionTierEnum


class UserBase(BaseModel):
    """Base model containing common user fields."""
    
    telegram_id: int
    name: Optional[str] = None
    role: Optional[str] = None
    industry: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list)
    goals: Optional[List[str]] = Field(default_factory=list)
    interests: Optional[List[str]] = Field(default_factory=list)


class UserCreate(UserBase):
    """
    Model for user registration/initial onboarding.
    
    Inherits all fields from UserBase, ensuring telegram_id is mandatory.
    The name field might be derived from Telegram user info during creation.
    """
    
    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "name": "John Doe",
                "role": "Software Engineer",
                "industry": "Technology",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "goals": ["Learn AI", "Network with professionals"],
                "interests": ["Machine Learning", "Web Development"]
            }
        }


class UserProfileUpdate(BaseModel):
    """
    Model for profile editing.
    
    All fields are optional to allow partial updates.
    telegram_id is excluded as it's not updatable.
    """
    
    name: Optional[str] = None
    role: Optional[str] = None
    industry: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list)
    goals: Optional[List[str]] = Field(default_factory=list)
    interests: Optional[List[str]] = Field(default_factory=list)
    
    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "role": "Senior Software Engineer",
                "industry": "Technology",
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "goals": ["Learn AI", "Network with professionals", "Start a tech blog"],
                "interests": ["Machine Learning", "Web Development", "Cloud Computing"]
            }
        }


class UserInDBBase(UserBase):
    """
    Base model for database representation of users.
    
    Includes all fields from UserBase plus additional database-specific fields.
    Uses telegram_id as the primary key.
    """
    
    social_points: int = 0
    free_requests_remaining: int = 5
    subscription_tier: Optional[str] = None
    subscription_expires_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    is_active_in_search: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "name": "John Doe",
                "role": "Software Engineer",
                "industry": "Technology",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "goals": ["Learn AI", "Network with professionals"],
                "interests": ["Machine Learning", "Web Development"],
                "social_points": 100,
                "free_requests_remaining": 3,
                "subscription_tier": "premium",
                "subscription_expires_at": "2024-12-31T23:59:59Z",
                "last_active_at": "2024-05-29T12:00:00Z",
                "is_active_in_search": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-05-29T12:00:00Z"
            }
        }


class UserResponse(UserInDBBase):
    """
    Model for API responses containing user data.
    
    Inherits all fields from UserInDBBase.
    This model will be used to return user data from the API endpoints.
    """
    
    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "name": "John Doe",
                "role": "Software Engineer",
                "industry": "Technology",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "goals": ["Learn AI", "Network with professionals"],
                "interests": ["Machine Learning", "Web Development"],
                "social_points": 100,
                "free_requests_remaining": 3,
                "subscription_tier": "premium",
                "subscription_expires_at": "2024-12-31T23:59:59Z",
                "last_active_at": "2024-05-29T12:00:00Z",
                "is_active_in_search": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-05-29T12:00:00Z"
            }
        } 