from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from ..config import get_supabase_url, get_supabase_key

class SupabaseClient:
    _instance = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialize the Supabase client with credentials from config."""
        if self._client is None:
            self._client = create_client(
                get_supabase_url(),
                get_supabase_key()
            )

    def fetch_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a user by their Telegram ID.
        
        Args:
            telegram_id (int): The Telegram user ID to search for
            
        Returns:
            Optional[Dict[str, Any]]: User data if found, None otherwise
        """
        try:
            response = self._client.table('users').select('*').eq('telegram_id', telegram_id).execute()
            print(f"Fetch user response: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            # Log the error here
            print(f"Error fetching user: {e}")
            return None

    def create_user(self, telegram_id: int, name: Optional[str] = None, defaults: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new user in the database.
        
        Args:
            telegram_id (int): The Telegram user ID
            name (Optional[str]): The user's name
            defaults (Optional[Dict[str, Any]]): Additional default values for the user
            
        Returns:
            Optional[Dict[str, Any]]: Created user data if successful, None otherwise
        """
        try:
            user_data = {
                'telegram_id': telegram_id,
                'name': name,
                'social_points': 0,
                'free_requests_remaining': 5,
                'is_active_in_search': True,
                'last_active_at': datetime.utcnow().isoformat()
            }
            
            if defaults:
                user_data.update(defaults)
            
            response = self._client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            # Log the error here
            print(f"Error creating user: {e}")
            return None

    def update_user_profile(self, telegram_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a user's profile data.
        
        Args:
            telegram_id (int): The Telegram user ID
            profile_data (Dict[str, Any]): The profile data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated user data if successful, None otherwise
        """
        try:
            # Validate profile data
            required_fields = {'name', 'role', 'industry', 'skills', 'goals', 'interests'}
            if not all(field in profile_data for field in required_fields):
                print(f"Missing required fields in profile data: {required_fields - set(profile_data.keys())}")
                return None
            
            # Update user profile
            response = self._client.table('users').update(profile_data).eq('telegram_id', telegram_id).execute()
            print(f"Update response: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            # Log the error here
            print(f"Error updating user profile: {e}")
            return None

    def fetch_user_profile(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a user's complete profile data.
        
        Args:
            telegram_id (int): The Telegram user ID
            
        Returns:
            Optional[Dict[str, Any]]: User profile data if found, None otherwise
        """
        try:
            # Select only profile-related fields
            profile_fields = [
                'name', 'role', 'industry', 'skills', 'goals', 'interests',
                'social_points', 'free_requests_remaining', 'is_active_in_search',
                'last_active_at'
            ]
            response = self._client.table('users').select(*profile_fields).eq('telegram_id', telegram_id).execute()
            print(f"Fetch profile response: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            # Log the error here
            print(f"Error fetching user profile: {e}")
            return None

    def update_user_last_active(self, telegram_id: int) -> bool:
        """
        Update a user's last active timestamp.
        
        Args:
            telegram_id (int): The Telegram user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self._client.table('users').update({
                'last_active_at': datetime.utcnow().isoformat()
            }).eq('telegram_id', telegram_id).execute()
            return bool(response.data)
        except Exception as e:
            # Log the error here
            print(f"Error updating user last active: {e}")
            return False

    def update_user_search_status(self, telegram_id: int, is_active: bool) -> bool:
        """
        Update a user's visibility in search.
        
        Args:
            telegram_id (int): The Telegram user ID
            is_active (bool): Whether the user should be visible in search
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self._client.table('users').update({
                'is_active_in_search': is_active
            }).eq('telegram_id', telegram_id).execute()
            return bool(response.data)
        except Exception as e:
            # Log the error here
            print(f"Error updating user search status: {e}")
            return False

    def get_inactive_users(self, days_threshold: int) -> list[Dict[str, Any]]:
        """
        Get users who haven't been active for the specified number of days.
        
        Args:
            days_threshold (int): Number of days of inactivity
            
        Returns:
            list[Dict[str, Any]]: List of inactive users
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_threshold)).isoformat()
            response = self._client.table('users').select('*').lt('last_active_at', cutoff_date).execute()
            return response.data
        except Exception as e:
            # Log the error here
            print(f"Error fetching inactive users: {e}")
            return [] 