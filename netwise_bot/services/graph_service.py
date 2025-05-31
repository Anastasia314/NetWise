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
            # Validate that both users exist
            inviter = await self._client.fetch_user_by_telegram_id(inviter_telegram_id)
            invitee = await self._client.fetch_user_by_telegram_id(invitee_telegram_id)
            
            if not inviter or not invitee:
                print(f"One or both users not found: inviter={bool(inviter)}, invitee={bool(invitee)}")
                return False
                
            # Check if connection already exists
            existing_connection = await self.get_connection(
                str(inviter_telegram_id),
                str(invitee_telegram_id)
            )
            
            if existing_connection:
                print(f"Connection already exists between {inviter_telegram_id} and {invitee_telegram_id}")
                return True  # Return True since the connection exists
                
            # Create a connection between the users
            connection = await self.create_connection(
                user1_id=str(inviter_telegram_id),
                user2_id=str(invitee_telegram_id),
                connection_type="intro_made",
                trust_score=1,  # Default trust score for new connections
                status="active"  # Direct connection through invite
            )
            
            if not connection:
                print(f"Failed to create connection between {inviter_telegram_id} and {invitee_telegram_id}")
                return False
                
            # Update last active for both users
            await self._client.update_user_last_active(inviter_telegram_id)
            await self._client.update_user_last_active(invitee_telegram_id)
            
            return True
            
        except Exception as e:
            print(f"Error processing invite: {e}")
            return False 

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
        Validate a connection type.
        
        Args:
            connection_type: Type of connection to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_types = ['worked_together', 'intro_made', 'met_at_event', 'other']
        return connection_type in valid_types

    def validate_trust_score(self, trust_score: int) -> bool:
        """
        Validate a trust score.
        
        Args:
            trust_score: Trust score to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return 1 <= trust_score <= 3 

    async def get_friends(
        self,
        telegram_id: int,
        trust_score: Optional[int] = None,
        connection_type: Optional[str] = None,
        sort_by: str = "name",
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Get first-degree connections (friends) for a user with filtering and pagination.
        
        Args:
            telegram_id: Telegram ID of the user
            trust_score: Optional filter by trust score
            connection_type: Optional filter by connection type
            sort_by: Field to sort by ('name', 'trust_score', 'created_at')
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            Dict containing:
            - connections: List of connection data with user details
            - total: Total number of connections
            - page: Current page
            - total_pages: Total number of pages
        """
        try:
            # Get user ID from telegram_id
            user = await self._client.fetch_user_by_telegram_id(telegram_id)
            if not user:
                raise ValueError("User not found")
                
            # Build query filters
            filters = []
            if trust_score is not None:
                filters.append(f"trust_score = {trust_score}")
            if connection_type is not None:
                filters.append(f"connection_type = '{connection_type}'")
                
            # Get connections with pagination
            connections = await self._client.fetch_connections(
                user['id'],
                filters=filters,
                sort_by=sort_by,
                page=page,
                per_page=per_page
            )
            
            # Get total count for pagination
            total = await self._client.count_connections(user['id'], filters=filters)
            
            # Calculate total pages
            total_pages = (total + per_page - 1) // per_page
            
            # Get user details for each connection
            for conn in connections['data']:
                other_user_id = conn['user2_id'] if conn['user1_id'] == user['id'] else conn['user1_id']
                other_user = await self._client.fetch_user_by_id(other_user_id)
                if other_user:
                    conn['user_details'] = other_user
                    
            return {
                'connections': connections['data'],
                'total': total,
                'page': page,
                'total_pages': total_pages
            }
            
        except Exception as e:
            print(f"Error getting friends: {e}")
            raise 