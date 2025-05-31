from typing import List, Dict, Any, Optional
from .supabase_client import SupabaseClient

class GraphService:
    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client

    async def create_connection(
        self,
        user1_id: str,
        user2_id: str,
        connection_type: str,
        trust_score: int,
        status: str = "pending"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new connection between two users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            connection_type: Type of connection ('worked_together', 'intro_made', 'met_at_event', 'other')
            trust_score: Trust score (1-3)
            status: Connection status ('pending', 'active', 'blocked')
            
        Returns:
            Dict containing the created connection data or None if creation failed
        """
        # Validate trust score
        if not 1 <= trust_score <= 3:
            raise ValueError("Trust score must be between 1 and 3")
            
        # Validate connection type
        valid_types = ['worked_together', 'intro_made', 'met_at_event', 'other']
        if connection_type not in valid_types:
            raise ValueError(f"Connection type must be one of: {', '.join(valid_types)}")
            
        # Validate status
        valid_statuses = ['pending', 'active', 'blocked']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
            
        # Ensure user1_id is always the smaller ID to maintain consistency
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
            
        return await self._client.create_connection(
            user1_id=user1_id,
            user2_id=user2_id,
            connection_type=connection_type,
            trust_score=trust_score,
            status=status
        )

    async def get_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all connections for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of connections where the user is either user1 or user2
        """
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

    async def process_invite(self, inviter_telegram_id: int, invitee_telegram_id: int) -> bool:
        """
        Process an invite when a new user joins through an invite link.
        
        Args:
            inviter_telegram_id: Telegram ID of the user who sent the invite
            invitee_telegram_id: Telegram ID of the user who accepted the invite
            
        Returns:
            bool: True if invite was processed successfully, False otherwise
        """
        try:
            # Create a connection between the users
            connection = await self.create_connection(
                user1_id=str(inviter_telegram_id),
                user2_id=str(invitee_telegram_id),
                connection_type="intro_made",
                trust_score=1,  # Default trust score for new connections
                status="active"  # Direct connection through invite
            )
            return bool(connection)
        except Exception as e:
            print(f"Error processing invite: {e}")
            return False 