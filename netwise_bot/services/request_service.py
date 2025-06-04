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
        telegram_id: int,
        page: int = 1,
        per_page: int = 5,
        status: Optional[str] = None,
        sort_by: str = "created_at"
    ) -> Dict[str, Any]:
        """Get user requests with pagination and filtering."""
        try:
            # Get user
            user = await self.supabase.fetch_user_by_telegram_id(telegram_id)
            if not user:
                return {"requests": [], "page": 1, "total_pages": 1}
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Fetch requests with pagination and filtering
            requests = await self.supabase.fetch_user_requests(
                user_id=user["id"],
                status=status,
                limit=per_page,
                offset=offset,
                sort_by=sort_by
            )
            
            # Get total count for pagination
            all_requests = await self.supabase.fetch_user_requests(
                user_id=user["id"],
                status=status
            )
            total_count = len(all_requests) if all_requests else 0
            
            # Calculate total pages
            total_pages = (total_count + per_page - 1) // per_page
            
            # Get helper and offer counts for each request
            for req in requests:
                matches = await self.supabase.fetch_request_matches(req["id"])
                req["helpers_count"] = len([m for m in matches if m["status"] == "accepted"])
                req["offers_count"] = len([m for m in matches if m["status"] == "pending"])
                
                # Convert string dates to datetime objects if needed
                for date_field in ["created_at", "updated_at", "expires_at"]:
                    if date_field in req and isinstance(req[date_field], str):
                        req[date_field] = datetime.fromisoformat(req[date_field].replace('Z', '+00:00'))
            
            return {
                "requests": requests,
                "page": page,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error fetching user requests: {e}")
            return {"requests": [], "page": 1, "total_pages": 1}

    async def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a single request by ID."""
        try:
            # Use fetch_user_requests with a filter for the specific request
            response = await self.supabase.fetch_user_requests(
                user_id=None,  # We don't filter by user here
                request_id=request_id
            )
            
            if response and len(response) > 0:
                request = response[0]
                
                # Get helper and offer counts
                matches = await self.supabase.fetch_request_matches(request_id)
                request["helpers_count"] = len([m for m in matches if m["status"] == "accepted"])
                request["offers_count"] = len(matches)
                
                return request
            return None
            
        except Exception as e:
            logger.error(f"Error getting request: {e}")
            return None

    async def update_request(
        self,
        request_id: str,
        description: str
    ) -> bool:
        """Update request description."""
        try:
            # Use the update_request_record method
            result = await self.supabase.update_request_record(
                request_id=request_id,
                data={
                    "description_text": description,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            return bool(result)

        except Exception as e:
            logger.error(f"Error updating request: {e}")
            return False

    async def delete_request(self, request_id: str) -> bool:
        """Soft delete request by updating status."""
        try:
            # Use the update_request_record method with the correct status
            result = await self.supabase.update_request_record(
                request_id=request_id,
                data={
                    "status": REQUEST_STATUS_CLOSED,  # Use the constant instead of "deleted"
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            return bool(result)

        except Exception as e:
            logger.error(f"Error deleting request: {e}")
            return False

    async def get_user_request_stats(self, telegram_id: int) -> Dict[str, Any]:
        """Get request statistics for user."""
        try:
            # Get user ID
            user = await self.supabase.fetch_user_by_telegram_id(telegram_id)
            if not user:
                return {
                    "total_requests": 0,
                    "open_requests": 0,
                    "pending_requests": 0,
                    "active_requests": 0,
                    "avg_response_time": 0,
                    "success_rate": 0
                }

            # Get all requests
            result = await self.supabase.table("requests").select(
                "id, status, created_at, updated_at"
            ).eq("requester_id", user["id"]).execute()

            requests = result.data if result else []
            
            # Calculate statistics
            total_requests = len(requests)
            open_requests = len([r for r in requests if r["status"] == "open"])
            pending_requests = len([r for r in requests if r["status"] == "pending_intro"])
            active_requests = len([r for r in requests if r["status"] in ["intro_made", "active"]])

            # Calculate average response time
            response_times = []
            for req in requests:
                if req["status"] in ["intro_made", "active"]:
                    created = datetime.fromisoformat(req["created_at"])
                    updated = datetime.fromisoformat(req["updated_at"])
                    response_times.append((updated - created).total_seconds() / 3600)  # Convert to hours

            avg_response_time = sum(response_times) / len(response_times) if response_times else 0

            # Calculate success rate
            successful_requests = len([r for r in requests if r["status"] in ["intro_made", "active"]])
            success_rate = (successful_requests / total_requests * 100) if total_requests else 0

            return {
                "total_requests": total_requests,
                "open_requests": open_requests,
                "pending_requests": pending_requests,
                "active_requests": active_requests,
                "avg_response_time": round(avg_response_time, 1),
                "success_rate": round(success_rate, 1)
            }

        except Exception as e:
            logger.error(f"Error getting request stats: {e}")
            return {
                "total_requests": 0,
                "open_requests": 0,
                "pending_requests": 0,
                "active_requests": 0,
                "avg_response_time": 0,
                "success_rate": 0
            }

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