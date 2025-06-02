from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import logging

from netwise_bot.services.supabase_client import SupabaseClient, supabase_client
from netwise_bot.services.user_service import user_service
from netwise_bot.utils.constants import (
    REQUEST_STATUS_OPEN,
    REQUEST_STATUS_PENDING_INTRO,
    REQUEST_STATUS_INTRO_MADE,
    REQUEST_STATUS_CLOSED,
    REQUEST_STATUS_EXPIRED
)
from netwise_bot.services.matching_service import MatchingService

logger = logging.getLogger(__name__)

class RequestService:
    def __init__(self, supabase_client: SupabaseClient, matching_service: MatchingService):
        self.supabase = supabase_client
        self.matching_service = matching_service

    async def create_request(self, requester_id: int, description: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new request for a user.
        
        Args:
            requester_id: The Telegram ID of the requester
            description: The request description
            
        Returns:
            Tuple of (success, message, request_id)
        """
        try:
            # Получаем пользователя по Telegram ID
            user = await self.supabase.fetch_user_by_telegram_id(requester_id)
            if not user:
                return False, "User not found.", None
            user_uuid = user['id']

            # Check if user has free requests remaining
            success = await user_service.add_free_request(requester_id)
            if not success:
                return False, "Failed to use free request.", None

            # Create request record
            request_data = {
                'requester_id': user_uuid,  # UUID вместо telegram_id
                'description_text': description,
                'status': REQUEST_STATUS_OPEN,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }

            result = await self.supabase.create_request_record(request_data)
            if not result:
                # If request creation fails, refund the free request
                await user_service.add_free_request(requester_id)
                return False, "Failed to create request. Please try again.", None

            request_id = result.get('id')
            if not request_id:
                # If no request ID returned, refund the free request
                await user_service.add_free_request(requester_id)
                return False, "Failed to create request. Please try again.", None

            logger.info(f"Created request {request_id} for user {user_uuid}")
            return True, "Request created successfully!", request_id

        except Exception as e:
            logger.error(f"Error creating request: {e}")
            # Try to refund the free request in case of error
            try:
                await user_service.add_free_request(requester_id)
            except Exception as refund_error:
                logger.error(f"Error refunding free request: {refund_error}")
            return False, "An error occurred while creating your request. Please try again.", None

    async def get_user_requests(
        self,
        user_id: int,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all requests for a user.
        
        Args:
            user_id: The Telegram ID of the user
            status: Optional status filter
            
        Returns:
            List of request data
        """
        try:
            # Получаем пользователя по Telegram ID
            user = await self.supabase.fetch_user_by_telegram_id(user_id)
            if not user:
                logger.error(f"User not found: {user_id}")
                return []
            user_uuid = user['id']
            return self.supabase.fetch_user_requests(user_uuid, status)
        except Exception as e:
            logger.error(f"Error fetching requests for user {user_id}: {e}")
            return []

    async def get_request(self, request_id: str) -> Optional[Dict]:
        """
        Get request details by ID.
        
        Args:
            request_id: The request ID
            
        Returns:
            Request data or None if not found
        """
        try:
            return await self.supabase.fetch_request(request_id)
        except Exception as e:
            logger.error(f"Error fetching request {request_id}: {e}")
            return None

    async def update_request_status(
        self,
        request_id: str,
        status: str
    ) -> bool:
        """
        Update request status.
        
        Args:
            request_id: The request ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.supabase.update_request_status(request_id, status)
        except Exception as e:
            logger.error(f"Error updating request {request_id} status: {e}")
            return False

    async def delete_request(self, request_id: UUID) -> bool:
        """
        Delete a request.
        
        Args:
            request_id: UUID of the request to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            await self.supabase.delete_request(request_id)
            logger.info(f"Deleted request {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting request {request_id}: {str(e)}")
            return False

    async def validate_request_description(self, description: str) -> tuple[bool, str]:
        """
        Validate a request description.
        
        Args:
            description: The request description to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not description:
            return False, "Request description cannot be empty."
            
        if len(description) < 10:
            return False, "Request description must be at least 10 characters long."
            
        if len(description) > 1000:
            return False, "Request description cannot exceed 1000 characters."
            
        return True, ""

    async def check_user_quota(self, telegram_id: int) -> tuple[bool, str]:
        """
        Check if a user has available request quota.
        
        Args:
            telegram_id: Telegram ID of the user
            
        Returns:
            Tuple of (has_quota, error_message)
        """
        try:
            user = await self.supabase.fetch_user_by_telegram_id(telegram_id)
            if not user:
                return False, "User not found."
                
            if user.get('free_requests_remaining', 0) <= 0:
                return False, "You have no free requests remaining. Please purchase more requests or wait for your monthly quota to reset."
                
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking user quota for {telegram_id}: {str(e)}")
            return False, "Error checking request quota. Please try again later."

    async def get_last_request_by_user(self, telegram_id: int) -> Optional[Dict]:
        """
        Get the most recent request for a user by their Telegram ID.
        
        Args:
            telegram_id: The Telegram ID of the user
            
        Returns:
            The most recent request data or None if not found
        """
        try:
            # Get user by Telegram ID
            user = await self.supabase.fetch_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User not found: {telegram_id}")
                return None
                
            # Get user's requests, ordered by creation date
            requests = self.supabase.fetch_user_requests(user['id'], limit=1)
            return requests[0] if requests else None
                
        except Exception as e:
            logger.error(f"Error getting last request for user {telegram_id}: {e}")
            return None

    async def get_requests_user_can_help_with(self, telegram_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get a list of requests that a user can help with based on their skills and connections.
        
        Args:
            telegram_id: The user's Telegram ID
            limit: Maximum number of requests to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant requests
        """
        try:
            # Get open requests not from this user
            response = await self.supabase.table('requests').select('*').eq('status', 'open').neq('requester_id', telegram_id).execute()
            open_requests = response.data

            if not open_requests:
                return []

            # Get user's profile for matching
            user_profile = await self.supabase.table('users').select('*').eq('telegram_id', telegram_id).single().execute()
            if not user_profile.data:
                logger.error(f"Could not find user profile for {telegram_id}")
                return []

            # Score and filter requests
            scored_requests = []
            for request in open_requests:
                # Skip requests older than 7 days
                if datetime.fromisoformat(request['created_at']) < datetime.now() - timedelta(days=7):
                    continue

                # Get match score
                score = await self.matching_service.calculate_match_score(
                    request['description_text'],
                    user_profile.data
                )

                if score > 0:  # Only include requests with some relevance
                    request['match_score'] = score
                    scored_requests.append(request)

            # Sort by match score and created_at
            scored_requests.sort(key=lambda x: (x['match_score'], x['created_at']), reverse=True)

            return scored_requests[:limit]

        except Exception as e:
            logger.error(f"Error getting requests for user {telegram_id}: {e}")
            return []

# Create singleton instance
request_service = RequestService(supabase_client, MatchingService()) 