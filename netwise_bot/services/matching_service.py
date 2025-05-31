"""
Matching service for finding potential helpers based on request descriptions.
"""
import logging
from typing import List, Dict, Tuple, Optional
from netwise_bot.services.supabase_client import supabase_client
from netwise_bot.services.graph_service import graph_service
from netwise_bot.services.user_service import user_service
from netwise_bot.utils.constants import (
    CONNECTION_TYPE_WORKED_TOGETHER,
    CONNECTION_TYPE_INTRO_MADE,
    CONNECTION_TYPE_MET_AT_EVENT,
    CONNECTION_TYPE_OTHER,
    MIN_TRUST_SCORE,
    MAX_TRUST_SCORE
)

logger = logging.getLogger(__name__)

class MatchingService:
    """Service for matching requests with potential helpers."""

    def __init__(self):
        """Initialize the matching service."""
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'with', 'by', 'about', 'like', 'through', 'over', 'before', 'between',
            'after', 'since', 'without', 'under', 'within', 'along', 'following',
            'across', 'behind', 'beyond', 'plus', 'except', 'but', 'up', 'down',
            'from', 'of', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
            'should', 'may', 'might', 'must', 'can', 'could', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my',
            'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours',
            'theirs', 'this', 'that', 'these', 'those', 'who', 'whom', 'whose',
            'which', 'what', 'where', 'when', 'why', 'how', 'all', 'any', 'both',
            'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
            'can', 'will', 'just', 'don', 'should', 'now'
        }

    async def extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extract relevant keywords from text.
        
        Args:
            text: The text to extract keywords from
            
        Returns:
            List of relevant keywords
        """
        try:
            # Convert to lowercase and split into words
            words = text.lower().split()
            
            # Remove stop words and short words
            keywords = [
                word for word in words
                if word not in self.stop_words and len(word) > 2
            ]
            
            # Remove duplicates while preserving order
            return list(dict.fromkeys(keywords))
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

    async def find_keyword_matches(
        self,
        request_description: str,
        requester_id: int
    ) -> List[Dict]:
        """
        Find potential helpers based on request description and user's network.
        
        Args:
            request_description: The request description text
            requester_id: The Telegram ID of the requester
            
        Returns:
            List of potential helpers with their match scores
        """
        try:
            # Get user by Telegram ID
            user = await supabase_client.fetch_user_by_telegram_id(requester_id)
            if not user:
                logger.error(f"User not found for Telegram ID: {requester_id}")
                return []

            # Get user's connections
            connections = await graph_service.get_connections(user['id'])
            if not connections:
                logger.info(f"No connections found for user {user['id']}")
                return []

            # Extract keywords from request description
            keywords = await self.extract_keywords_from_text(request_description)
            if not keywords:
                logger.info("No keywords extracted from request description")
                return []

            potential_helpers = []
            for connection in connections:
                # Determine which user is the helper
                helper_id = connection['user2_id'] if connection['user1_id'] == user['id'] else connection['user1_id']
                
                # Get helper's profile
                helper = await supabase_client.get_user_by_id(helper_id)
                if not helper:
                    continue

                # Calculate match score based on skills, interests, and goals
                score = 0
                
                # Helper's skills matching request keywords
                if helper.get('skills'):
                    for skill in helper['skills']:
                        if skill and any(keyword in skill.lower() for keyword in keywords):
                            score += 2

                # Helper's interests matching request keywords
                if helper.get('interests'):
                    for interest in helper['interests']:
                        if interest and any(keyword in interest.lower() for keyword in keywords):
                            score += 1

                # Helper's goals matching request keywords
                if helper.get('goals'):
                    for goal in helper['goals']:
                        if goal and any(keyword in goal.lower() for keyword in keywords):
                            score += 1

                if score > 0:
                    potential_helpers.append({
                        'user_id': helper_id,
                        'name': helper.get('name', 'Unknown'),
                        'role': helper.get('role', ''),
                        'connection_type': connection.get('connection_type', ''),
                        'trust_score': connection.get('trust_score', 0),
                        'score': score
                    })

            # Sort by score
            potential_helpers.sort(key=lambda x: x['score'], reverse=True)
            return potential_helpers

        except Exception as e:
            logger.error(f"Error finding keyword matches: {str(e)}")
            return []

    async def _calculate_match_score(
        self,
        keywords: List[str],
        profile: Dict,
        connection_type: str,
        trust_score: int
    ) -> float:
        """
        Calculate match score for a potential helper.
        
        Args:
            keywords: List of keywords from request
            profile: Helper's profile data
            connection_type: Type of connection
            trust_score: Trust score of connection
            
        Returns:
            Match score (float)
        """
        try:
            score = 0.0
            
            # Check keywords against profile fields
            profile_fields = {
                'skills': 2.0,  # Highest weight for skills
                'role': 1.5,    # High weight for role
                'industry': 1.5, # High weight for industry
                'goals': 1.0,   # Medium weight for goals
                'interests': 1.0 # Medium weight for interests
            }
            
            for field, weight in profile_fields.items():
                field_value = profile.get(field, '')
                if isinstance(field_value, list):
                    field_value = ' '.join(field_value)
                
                field_value = field_value.lower()
                for keyword in keywords:
                    if keyword in field_value:
                        score += weight

            # Weight by connection type
            connection_weights = {
                CONNECTION_TYPE_WORKED_TOGETHER: 1.5,
                CONNECTION_TYPE_INTRO_MADE: 1.2,
                CONNECTION_TYPE_MET_AT_EVENT: 1.1,
                CONNECTION_TYPE_OTHER: 1.0
            }
            score *= connection_weights.get(connection_type, 1.0)

            # Weight by trust score
            trust_weight = (trust_score - MIN_TRUST_SCORE + 1) / (MAX_TRUST_SCORE - MIN_TRUST_SCORE + 1)
            score *= (1 + trust_weight)

            return round(score, 2)

        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0.0

# Create singleton instance
matching_service = MatchingService() 