from typing import Optional, Dict, Any, List
from .supabase_client import SupabaseClient

class ConnectionService:
    def __init__(self):
        self._client = SupabaseClient()

    async def create_connection(
        self,
        user1_id: str,
        user2_id: str,
        connection_type: str,
        trust_score: int,
        status: str = "active"
    ) -> bool:
        """
        Create a new connection between users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            connection_type: Type of connection (e.g., "invite", "search")
            trust_score: Initial trust score for the connection
            status: Connection status (default: "active")
            
        Returns:
            bool: True if connection was created successfully
        """
        try:
            # Check if connection already exists
            existing = await self._client.fetch_connections(user1_id)
            for conn in existing:
                if conn['user1_id'] == user1_id and conn['user2_id'] == user2_id:
                    return True
                if conn['user1_id'] == user2_id and conn['user2_id'] == user1_id:
                    return True
            
            # Create new connection
            connection = await self._client.create_connection(
                user1_id=user1_id,
                user2_id=user2_id,
                connection_type=connection_type,
                trust_score=trust_score,
                status=status
            )
            
            return bool(connection)
            
        except Exception as e:
            print(f"Error creating connection: {e}")
            return False

    async def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all connections for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of connection dictionaries
        """
        try:
            return await self._client.fetch_connections(user_id)
        except Exception as e:
            print(f"Error getting user connections: {e}")
            return []

    async def update_connection_trust(
        self,
        connection_id: str,
        new_trust_score: int
    ) -> bool:
        """
        Update the trust score of a connection.
        
        Args:
            connection_id: ID of the connection
            new_trust_score: New trust score value
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Update connection in database
            success = await self._client.update_connection(
                connection_id=connection_id,
                updates={'trust_score': new_trust_score}
            )
            
            return bool(success)
            
        except Exception as e:
            print(f"Error updating connection trust: {e}")
            return False

    async def delete_connection(self, connection_id: str) -> bool:
        """
        Delete a connection.
        
        Args:
            connection_id: ID of the connection to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Delete connection from database
            success = await self._client.delete_connection(connection_id)
            
            return bool(success)
            
        except Exception as e:
            print(f"Error deleting connection: {e}")
            return False 