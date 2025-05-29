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

from models.common_models import SubscriptionTierEnum


class UserBase(BaseModel):
    """Base model containing common user fields."""
    
    telegram_id: int = Field(description="Unique identifier for the user from Telegram")
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    role: Optional[str] = Field(None, max_length=100, description="User's professional role or job title")
    industry: Optional[str] = Field(None, max_length=100, description="User's industry or sector")
    skills: List[str] = Field(default_factory=list, description="List of user's professional skills")
    goals: List[str] = Field(default_factory=list, description="List of user's professional goals")
    interests: List[str] = Field(default_factory=list, description="List of user's professional interests")


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
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    
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
    
    social_points: int = Field(0, description="User's accumulated social points for engagement")
    free_requests_remaining: int = Field(5, description="Number of free API requests remaining")
    subscription_tier: str = Field("free", description="User's current subscription tier")
    subscription_expires_at: Optional[datetime] = Field(None, description="Expiration date of the user's subscription")
    last_active_at: Optional[datetime] = Field(None, description="Timestamp of user's last activity")
    is_active_in_search: bool = Field(True, description="Whether the user is discoverable in search")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last profile update")
    
    class Config:
        """Pydantic model configuration."""
        
        from_attributes = True
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