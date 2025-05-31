from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .supabase_client import SupabaseClient

class UserService:
    def __init__(self):
        self._client = SupabaseClient()

    async def get_or_create_user(self, telegram_id: int, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a user by Telegram ID or create if not exists.
        
        Args:
            telegram_id: Telegram ID of the user
            name: Optional name of the user
            
        Returns:
            User data dictionary or None if operation failed
        """
        try:
            # Try to get existing user
            user = await self._client.fetch_user_by_telegram_id(telegram_id)
            
            if user:
                return user
                
            # Create new user if doesn't exist
            return await self._client.create_user(
                telegram_id=telegram_id,
                name=name,
                defaults={
                    "social_points": 0,
                    "free_requests_remaining": 5,
                    "is_active_in_search": True
                }
            )
        except Exception as e:
            print(f"Error in get_or_create_user: {e}")
            return None

    async def get_profile(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user profile by Telegram ID.
        
        Args:
            telegram_id: Telegram ID of the user
            
        Returns:
            Profile data dictionary or None if not found
        """
        try:
            return await self._client.fetch_user_profile(telegram_id)
        except Exception as e:
            print(f"Error in get_profile: {e}")
            return None

    async def update_profile(self, telegram_id: int, profile_data: Dict[str, Any]) -> bool:
        """
        Update user profile.
        
        Args:
            telegram_id: Telegram ID of the user
            profile_data: Dictionary containing profile fields to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            return bool(await self._client.update_user_profile(telegram_id, profile_data))
        except Exception as e:
            print(f"Error in update_profile: {e}")
            return False

    async def update_user_activity(self, telegram_id: int) -> bool:
        """
        Update user's last active timestamp.
        
        Args:
            telegram_id: Telegram ID of the user
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            return bool(await self._client.update_user_last_active(telegram_id))
        except Exception as e:
            print(f"Error in update_user_activity: {e}")
            return False

    async def set_search_status(self, telegram_id: int, is_active: bool) -> bool:
        """
        Set user's visibility in search.
        
        Args:
            telegram_id: Telegram ID of the user
            is_active: Whether user should be visible in search
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            return bool(await self._client.update_user_search_status(telegram_id, is_active))
        except Exception as e:
            print(f"Error in set_search_status: {e}")
            return False

    def get_inactive_users(self, days_threshold: int = 30) -> List[Dict[str, Any]]:
        """
        Get users who haven't been active for the specified number of days.
        
        Args:
            days_threshold (int): Number of days of inactivity (default: 30)
            
        Returns:
            List[Dict[str, Any]]: List of inactive users
        """
        return self._client.get_inactive_users(days_threshold)

    def _validate_profile_data(self, profile_data: Dict[str, Any]) -> bool:
        """
        Validate profile data before updating.
        
        Args:
            profile_data (Dict[str, Any]): The profile data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = {'name', 'role', 'industry', 'skills', 'goals', 'interests'}
        if not all(field in profile_data for field in required_fields):
            return False

        # Validate field types
        if not isinstance(profile_data['name'], str) or not profile_data['name'].strip():
            return False
        if not isinstance(profile_data['role'], str) or not profile_data['role'].strip():
            return False
        if not isinstance(profile_data['industry'], str) or not profile_data['industry'].strip():
            return False
        if not isinstance(profile_data['skills'], list) or not all(isinstance(s, str) for s in profile_data['skills']):
            return False
        if not isinstance(profile_data['goals'], list) or not all(isinstance(g, str) for g in profile_data['goals']):
            return False
        if not isinstance(profile_data['interests'], list) or not all(isinstance(i, str) for i in profile_data['interests']):
            return False

        return True 