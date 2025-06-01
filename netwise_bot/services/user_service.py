from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .supabase_client import SupabaseClient
from netwise_bot.utils.constants import POINTS_PER_HELP, FREE_REQUESTS_PER_MONTH
import logging

# Initialize logger
logger = logging.getLogger(__name__)

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
                    "is_active_in_search": False  # Default to not visible in search
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

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by their UUID.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dict containing user data or None if not found
        """
        try:
            return await self._client.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    async def add_social_points(self, telegram_id: int, points: int = POINTS_PER_HELP) -> bool:
        """
        Add social points to a user's account.
        Points can only be earned by helping others, not spent.
        
        Args:
            telegram_id: The Telegram ID of the user
            points: The number of points to add (default: POINTS_PER_HELP)
            
        Returns:
            bool: True if points were added successfully, False otherwise
        """
        try:
            if points <= 0:
                logger.warning(f"Attempted to add non-positive points: {points}")
                return False

            result = await self._client.update_user_social_points(telegram_id, points)
            return result is not None

        except Exception as e:
            logger.error(f"Error adding social points: {e}")
            return False

    async def get_social_points(self, telegram_id: int) -> Optional[int]:
        """
        Get the current social points for a user.
        
        Args:
            telegram_id: The Telegram ID of the user
            
        Returns:
            int: The number of social points, or None if user not found
        """
        try:
            user = await self._client.fetch_user_by_telegram_id(telegram_id)
            if not user:
                return None
            return user.get('social_points', 0)
        except Exception as e:
            logger.error(f"Error getting social points: {e}")
            return None

    async def add_free_request(self, telegram_id: int) -> bool:
        """
        Add a free request to a user's quota.
        Args:
            telegram_id: Telegram ID of the user
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Получаем пользователя по Telegram ID
            user = await self._client.fetch_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found: {telegram_id}")
                return False
            user_uuid = user['id']
            # Обновляем количество бесплатных запросов
            result = self._client.update_user_free_requests(user_uuid, 1)
            return result is not None
        except Exception as e:
            logger.error(f"Error adding free request: {e}")
            return False

    async def reset_monthly_free_requests(self) -> bool:
        """
        Reset free requests for all users to the default value.
        
        Returns:
            bool: True if reset was successful, False otherwise
        """
        try:
            result = await self._client.reset_all_users_free_requests()
            return bool(result)
        except Exception as e:
            logger.error(f"Error resetting free requests: {e}")
            return False

    async def get_connection_type(self, user1_id: str, user2_id: str) -> Optional[str]:
        """
        Get the type of connection between two users.
        
        Args:
            user1_id: The UUID of the first user
            user2_id: The UUID of the second user
            
        Returns:
            "direct" if users are directly connected,
            "indirect" if users are connected through a common connection,
            None if no connection exists
        """
        try:
            # Check for direct connection
            connections = await self._client.fetch_connections(user1_id)
            for conn in connections:
                if (conn['user1_id'] == user1_id and conn['user2_id'] == user2_id) or \
                   (conn['user1_id'] == user2_id and conn['user2_id'] == user1_id):
                    return "direct"

            # Check for indirect connection
            user1_connections = await self._client.fetch_connections(user1_id)
            user2_connections = await self._client.fetch_connections(user2_id)
            
            # Get sets of connected user IDs
            user1_connected_ids = {conn['user2_id'] if conn['user1_id'] == user1_id else conn['user1_id'] 
                                 for conn in user1_connections}
            user2_connected_ids = {conn['user2_id'] if conn['user1_id'] == user2_id else conn['user1_id'] 
                                 for conn in user2_connections}
            
            # Check for common connections
            if user1_connected_ids.intersection(user2_connected_ids):
                return "indirect"

            return None

        except Exception as e:
            logger.error(f"Error getting connection type: {e}")
            return None

    async def get_common_connection(
        self,
        user1_id: int,
        user2_id: int
    ) -> Optional[Dict]:
        """
        Get the common connection between two users.
        
        Args:
            user1_id: The Telegram ID of the first user
            user2_id: The Telegram ID of the second user
            
        Returns:
            Dict containing the common connection's details if found,
            None otherwise
        """
        try:
            # Get connections for both users
            connections = await self._client.fetch_connections(user1_id, user2_id)
            if not connections:
                return None

            # Find common connection
            common_id = connections[0]['id']
            user_details = await self._client.fetch_user_details(common_id)

            if user_details:
                return user_details

            return None

        except Exception as e:
            logger.error(f"Error getting common connection: {e}")
            return None

# Create singleton instance
user_service = UserService() 