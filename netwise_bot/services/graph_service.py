from typing import List, Dict, Any, Optional
from .supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client

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
            status: Connection status (default: "active")
            
        Returns:
            Dict containing connection data if successful, None otherwise
        """
        try:
            logger.info(f"Creating connection: user1={user1_id}, user2={user2_id}, type={connection_type}, trust={trust_score}")
            
            # Validate connection type and trust score
            if not self.validate_connection_type(connection_type):
                logger.error(f"Invalid connection type: {connection_type}")
                raise ValueError("Invalid connection type")
                
            if not self.validate_trust_score(trust_score):
                logger.error(f"Invalid trust score: {trust_score}")
                raise ValueError("Invalid trust score")
                
            # Create connection using supabase client
            connection = await self._client.create_connection(
            user1_id=user1_id,
            user2_id=user2_id,
            connection_type=connection_type,
            trust_score=trust_score,
            status=status
        )

            logger.info(f"Connection created: {connection}")
            return connection
            
        except Exception as e:
            logger.error(f"Error creating connection: {e}", exc_info=True)
            return None

    async def get_connections(self, user_id: str, is_telegram_id: bool = False) -> List[Dict[str, Any]]:
        """
        Get all connections for a user.
        Args:
            user_id: ID of the user (UUID or Telegram ID)
            is_telegram_id: If True, user_id is Telegram ID and will be converted to UUID
        Returns:
            List of connections where the user is either user1 or user2
        """
        if is_telegram_id:
            user = await self._client.fetch_user_by_telegram_id(user_id)
            if not user:
                return []
            user_id = user['id']
        return await self._client.fetch_connections(user_id)

    async def get_connection(self, user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific connection between two users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            Connection data if exists, None otherwise
        """
        # Ensure user1_id is always the smaller ID to maintain consistency
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
            
        connections = await self._client.fetch_connections(user1_id)
        for conn in connections:
            if (conn['user1_id'] == user1_id and conn['user2_id'] == user2_id) or \
               (conn['user1_id'] == user2_id and conn['user2_id'] == user1_id):
                return conn
        return None 

    async def generate_invite_link(self, telegram_id: int) -> Optional[str]:
        """
        Generate an invite link for a user.
        
        Args:
            telegram_id: Telegram ID of the user generating the invite
            
        Returns:
            Invite link string or None if generation failed
        """
        try:
            # Get bot username from config
            bot_username = get_bot_username()
            if not bot_username:
                return None
                
            # Generate invite link
            invite_link = f"https://t.me/{bot_username}?start=invite_{telegram_id}"
            return invite_link
        except Exception as e:
            print(f"Error generating invite link: {e}")
            return None

    async def process_invite(
        self,
        inviter_telegram_id: int,
        invitee_telegram_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Process an invite between two users.
        
        Args:
            inviter_telegram_id: Telegram ID of the inviter
            invitee_telegram_id: Telegram ID of the invitee
            
        Returns:
            Dict containing user IDs and inviter name if successful, None otherwise
        """
        try:
            logger.info(f"Processing invite: inviter={inviter_telegram_id}, invitee={invitee_telegram_id}")
            
            # Get users by telegram IDs
            inviter = await self._client.fetch_user_by_telegram_id(inviter_telegram_id)
            invitee = await self._client.fetch_user_by_telegram_id(invitee_telegram_id)
            
            logger.info(f"Fetched users: inviter={inviter}, invitee={invitee}")
            
            if not inviter:
                logger.error(f"Inviter not found: {inviter_telegram_id}")
                return None
                
            if not invitee:
                logger.error(f"Invitee not found: {invitee_telegram_id}")
                return None
                
            # Get UUIDs
            inviter_uuid = inviter['id']
            invitee_uuid = invitee['id']
            logger.info(f"User UUIDs: inviter={inviter_uuid}, invitee={invitee_uuid}")
            
            # Check if connection already exists
            existing = await self._client.fetch_connections(inviter_uuid)
            logger.info(f"Existing connections: {existing}")
            
            for conn in existing:
                if (conn['user1_id'] == inviter_uuid and conn['user2_id'] == invitee_uuid) or \
                   (conn['user1_id'] == invitee_uuid and conn['user2_id'] == inviter_uuid):
                    logger.info(f"Connection already exists between {inviter_uuid} and {invitee_uuid}")
                    return None
            
            # Return user IDs for FSM flow
            result = {
                'user1_id': inviter_uuid,
                'user2_id': invitee_uuid,
                'inviter_name': inviter.get('name', 'User')
            }
            logger.info(f"Returning result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing invite: {e}", exc_info=True)
            return None

    async def update_connection_details(
        self,
        user1_id: str,
        user2_id: str,
        connection_type: str,
        trust_score: int
    ) -> Optional[Dict[str, Any]]:
        """
        Update the details of an existing connection.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            connection_type: Type of connection ('worked_together', 'intro_made', 'met_at_event', 'other')
            trust_score: Trust score (1-3)
            
        Returns:
            Dict containing the updated connection data or None if update failed
        """
        # Validate trust score
        if not 1 <= trust_score <= 3:
            raise ValueError("Trust score must be between 1 and 3")
            
        # Validate connection type
        valid_types = ['worked_together', 'intro_made', 'met_at_event', 'other']
        if connection_type not in valid_types:
            raise ValueError(f"Connection type must be one of: {', '.join(valid_types)}")
            
        # Ensure user1_id is always the smaller ID to maintain consistency
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
            
        # Get existing connection
        connection = await self.get_connection(user1_id, user2_id)
        if not connection:
            raise ValueError("Connection does not exist")
            
        # Update connection
        return await self._client.update_connection(
            connection['id'],
            {
                'connection_type': connection_type,
                'trust_score': trust_score
            }
        )

    def validate_connection_type(self, connection_type: str) -> bool:
        """
        Validate if the connection type is valid.
        
        Args:
            connection_type: Type of connection to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_types = {'worked_together', 'intro_made', 'personal_contact', 'chat_help'}
        return connection_type in valid_types

    def validate_trust_score(self, trust_score: int) -> bool:
        """
        Validate if the trust score is valid.
        
        Args:
            trust_score: Trust score to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(trust_score, int) and 1 <= trust_score <= 3

    async def get_friends(
        self,
        telegram_id: int,
        page: int = 1,
        per_page: int = 10,
        trust_score: Optional[int] = None,
        sort_by: str = "name"
    ) -> Dict[str, Any]:
        """
        Get user's connections with pagination and filtering.
        
        Args:
            telegram_id: Telegram ID of the user
            page: Page number (1-based)
            per_page: Number of items per page
            trust_score: Optional trust score filter
            sort_by: Field to sort by (name, trust_score, created_at)
            
        Returns:
            Dict containing connections list and pagination info
        """
        try:
            logger.info(f"Getting friends for user {telegram_id}, page {page}")
            
            # Get user by telegram ID
            user = await self._client.fetch_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found: {telegram_id}")
                return {'connections': [], 'total': 0, 'page': 1, 'total_pages': 1}
                
            # Get all connections
            connections = await self._client.fetch_connections(user['id'])
            logger.info(f"Found {len(connections)} connections")
            
            # Filter by trust score if specified
            if trust_score is not None:
                connections = [c for c in connections if c['trust_score'] == trust_score]
                logger.info(f"Filtered to {len(connections)} connections with trust score {trust_score}")
            
            # Get user details for each connection
            for conn in connections:
                other_user_id = conn['user2_id'] if conn['user1_id'] == user['id'] else conn['user1_id']
                other_user = await self._client.get_user_by_id(other_user_id)
                conn['user_details'] = other_user
                
            # Sort connections
            if sort_by == "name":
                connections.sort(key=lambda x: x['user_details'].get('name', ''))
            elif sort_by == "trust_score":
                connections.sort(key=lambda x: x['trust_score'], reverse=True)
            elif sort_by == "created_at":
                connections.sort(key=lambda x: x['created_at'], reverse=True)
                
            # Calculate pagination
            total = len(connections)
            total_pages = (total + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            # Get page of connections
            page_connections = connections[start_idx:end_idx]
            
            return {
                'connections': page_connections,
                'total': total,
                'page': page,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting friends: {e}", exc_info=True)
            return {'connections': [], 'total': 0, 'page': 1, 'total_pages': 1} 