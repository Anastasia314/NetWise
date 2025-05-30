from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .supabase_client import SupabaseClient

class UserService:
    def __init__(self):
        self._supabase = SupabaseClient()

    def get_or_create_user(self, telegram_id: int, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get an existing user or create a new one if they don't exist.
        
        Args:
            telegram_id (int): The Telegram user ID
            name (Optional[str]): The user's name
            
        Returns:
            Optional[Dict[str, Any]]: User data if successful, None otherwise
        """
        user = self._supabase.fetch_user_by_telegram_id(telegram_id)
        if not user:
            user = self._supabase.create_user(telegram_id, name)
        return user

    def update_profile(self, telegram_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a user's profile data.
        
        Args:
            telegram_id (int): The Telegram user ID
            profile_data (Dict[str, Any]): The profile data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated user data if successful, None otherwise
        """
        if not self._validate_profile_data(profile_data):
            return None
        return self._supabase.update_user_profile(telegram_id, profile_data)

    def get_profile(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user's complete profile data.
        
        Args:
            telegram_id (int): The Telegram user ID
            
        Returns:
            Optional[Dict[str, Any]]: User profile data if found, None otherwise
        """
        return self._supabase.fetch_user_profile(telegram_id)

    def update_last_active(self, telegram_id: int) -> bool:
        """
        Update a user's last active timestamp.
        
        Args:
            telegram_id (int): The Telegram user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._supabase.update_user_last_active(telegram_id)

    def set_search_status(self, telegram_id: int, is_active: bool) -> bool:
        """
        Set a user's visibility in search.
        
        Args:
            telegram_id (int): The Telegram user ID
            is_active (bool): Whether the user should be visible in search
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._supabase.update_user_search_status(telegram_id, is_active)

    def get_inactive_users(self, days_threshold: int = 30) -> List[Dict[str, Any]]:
        """
        Get users who haven't been active for the specified number of days.
        
        Args:
            days_threshold (int): Number of days of inactivity (default: 30)
            
        Returns:
            List[Dict[str, Any]]: List of inactive users
        """
        return self._supabase.get_inactive_users(days_threshold)

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