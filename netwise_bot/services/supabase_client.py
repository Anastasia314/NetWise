from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from supabase import create_client, Client
from ..config import get_supabase_url, get_supabase_key
from uuid import UUID
from netwise_bot.utils.constants import FREE_REQUESTS_PER_MONTH

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

    async def fetch_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
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

    async def create_user(self, telegram_id: int, name: Optional[str] = None, defaults: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
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

    async def update_user_profile(self, telegram_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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

    async def fetch_user_profile(self, telegram_id: int) -> Optional[Dict[str, Any]]:
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

    async def update_user_last_active(self, telegram_id: int) -> bool:
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

    async def update_user_search_status(self, telegram_id: int, is_active: bool) -> bool:
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

    async def create_connection(
        self,
        user1_id: str,
        user2_id: str,
        connection_type: str,
        trust_score: int,
        status: str = "active"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new connection between two users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            connection_type: Type of connection
            trust_score: Trust score (1-3)
            status: Connection status
            
        Returns:
            Dict containing the created connection data or None if creation failed
        """
        try:
            data = {
                "user1_id": user1_id,
                "user2_id": user2_id,
                "connection_type": connection_type,
                "trust_score": trust_score,
                "status": status
            }
            response = self._client.table('connections').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating connection: {e}")
            return None

    async def fetch_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all connections for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of connections where the user is either user1 or user2
        """
        try:
            # Query connections where user is either user1 or user2
            response = self._client.table('connections').select('*').or_(
                f'user1_id.eq.{user_id},user2_id.eq.{user_id}'
            ).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching connections: {e}")
            return []

    async def update_connection(self, connection_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a connection's data."""
        try:
            response = self._client.table('connections').update(updates).eq('id', connection_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating connection: {e}")
            return None

    async def delete_connection(self, connection_id: str) -> bool:
        """Delete a connection."""
        try:
            response = self._client.table('connections').delete().eq('id', connection_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting connection: {e}")
            return False

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by their ID."""
        try:
            response = self._client.table('users').select('*').eq('id', user_id).execute()
            users = response.data
            return users[0] if users else None
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None

    async def create_request_record(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new request record in the database.
        
        Args:
            request_data: Dictionary containing request data
            
        Returns:
            Created request record
        """
        try:
            result = self._client.table("requests").insert(request_data).execute()
            return result.data[0]
        except Exception as e:
            print(f"Error creating request record: {str(e)}")
            raise

    def fetch_user_requests(
        self,
        requester_id: int,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch requests for a specific user.
        Args:
            requester_id: Telegram ID of the user
            status: Optional filter by request status
            limit: Maximum number of requests to return
            offset: Number of requests to skip
        Returns:
            List of request records
        """
        try:
            query = self._client.table("requests").select("*").eq("requester_id", requester_id)
            if status:
                query = query.eq("status", status)
            result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            print(f"Error fetching user requests: {str(e)}")
            raise

    async def fetch_request(self, request_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific request by ID.
        
        Args:
            request_id: UUID of the request
            
        Returns:
            Request record or None if not found
        """
        try:
            result = await self._client.table("requests").select("*").eq("id", str(request_id)).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error fetching request: {str(e)}")
            raise

    async def update_request_status(self, request_id: UUID, new_status: str) -> None:
        """
        Update the status of a request.
        
        Args:
            request_id: UUID of the request
            new_status: New status to set
        """
        try:
            await self._client.table("requests").update({"status": new_status}).eq("id", str(request_id)).execute()
            
        except Exception as e:
            print(f"Error updating request status: {str(e)}")
            raise

    async def delete_request(self, request_id: UUID) -> None:
        """
        Delete a request.
        
        Args:
            request_id: UUID of the request to delete
        """
        try:
            await self._client.table("requests").delete().eq("id", str(request_id)).execute()
            
        except Exception as e:
            print(f"Error deleting request: {str(e)}")
            raise

    async def update_user_social_points(self, telegram_id: int, points_change: int) -> Optional[Dict[str, Any]]:
        """
        Update a user's social points.
        
        Args:
            telegram_id: Telegram ID of the user
            points_change: Amount to add (positive) or subtract (negative)
            
        Returns:
            Updated user data or None if update failed
        """
        try:
            # First get current points to ensure we don't go negative
            user = await self.fetch_user_by_telegram_id(telegram_id)
            if not user:
                print(f"User {telegram_id} not found when updating social points")
                return None
                
            current_points = user.get('social_points', 0)
            new_points = current_points + points_change
            
            if new_points < 0:
                print(f"Cannot update social points for user {telegram_id}: would result in negative points")
                return None
                
            result = await self._client.table('users').update({
                'social_points': new_points
            }).eq('telegram_id', telegram_id).execute()
            
            if result.data:
                print(f"Updated social points for user {telegram_id}: {current_points} -> {new_points}")
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error updating social points for user {telegram_id}: {str(e)}")
            return None

    async def update_user_free_requests(self, telegram_id: int, change: int) -> Optional[Dict[str, Any]]:
        """
        Update a user's free requests remaining.
        
        Args:
            telegram_id: Telegram ID of the user
            change: Amount to add (positive) or subtract (negative)
            
        Returns:
            Updated user data or None if update failed
        """
        try:
            # First get current free requests to ensure we don't go negative
            user = await self.fetch_user_by_telegram_id(telegram_id)
            if not user:
                print(f"User {telegram_id} not found when updating free requests")
                return None
                
            current_requests = user.get('free_requests_remaining', 0)
            new_requests = current_requests + change
            
            if new_requests < 0:
                print(f"Cannot update free requests for user {telegram_id}: would result in negative requests")
                return None
                
            result = await self._client.table('users').update({
                'free_requests_remaining': new_requests
            }).eq('telegram_id', telegram_id).execute()
            
            if result.data:
                print(f"Updated free requests for user {telegram_id}: {current_requests} -> {new_requests}")
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error updating free requests for user {telegram_id}: {str(e)}")
            return None

    async def reset_all_users_free_requests(self) -> bool:
        """
        Reset free requests for all users to the default value.
        
        Returns:
            True if reset was successful, False otherwise
        """
        try:
            result = await self._client.table('users').update({
                'free_requests_remaining': FREE_REQUESTS_PER_MONTH
            }).execute()
            
            if result.data:
                print(f"Reset free requests for all users to {FREE_REQUESTS_PER_MONTH}")
                return True
            return False
            
        except Exception as e:
            print(f"Error resetting free requests for all users: {str(e)}")
            return False

    async def log_request_match(
        self,
        request_id: str,
        suggested_user_uuid: str,
        introducer_user_uuid: Optional[str] = None,
        match_score: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Log a request match in the database.
        
        Args:
            request_id: The request ID
            suggested_user_uuid: UUID of the suggested helper
            introducer_user_uuid: Optional UUID of the introducer
            match_score: The match score for this helper
            
        Returns:
            Dict containing the created match data or None if creation failed
        """
        try:
            data = {
                "request_id": request_id,
                "suggested_user_id": suggested_user_uuid,
                "status": "suggested",
                "match_score": match_score
            }
            
            if introducer_user_uuid:
                data["introducer_user_id"] = introducer_user_uuid

            response = self._client.table("request_matches_log").insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error logging request match: {e}")
            return None

    async def update_request_match_status(
        self,
        request_id: str,
        suggested_user_uuid: str,
        status: str,
        introducer_user_uuid: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update the status of a request match.
        
        Args:
            request_id: The request ID
            suggested_user_uuid: UUID of the suggested helper
            status: The new status
            introducer_user_uuid: Optional UUID of the introducer
            
        Returns:
            Dict containing the updated match data or None if update failed
        """
        try:
            query = self._client.table("request_matches_log").update(
                {"status": status}
            ).match({
                "request_id": request_id,
                "suggested_user_id": suggested_user_uuid
            })
            
            if introducer_user_uuid:
                query = query.match({"introducer_user_id": introducer_user_uuid})

            response = query.execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error updating request match status: {e}")
            return None

# Create singleton instance
supabase_client = SupabaseClient() 