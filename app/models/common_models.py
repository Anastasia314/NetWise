"""
Common models and enumerations used across the application.

This module contains shared models and enumerations that are used by multiple
other model modules. Currently includes subscription tier enumerations.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SubscriptionTierEnum(str, Enum):
    """
    Enumeration of available subscription tiers.
    
    Each tier represents a different level of service with its own
    set of features and limitations. The values are used in the
    subscription_tier field of the UserInDBBase model.
    """
    
    FREE = "free"  # Basic tier with limited features
    TIER_500 = "tier_500"  # Mid-tier with 500 requests per month
    TIER_1000 = "tier_1000"  # Premium tier with 1000 requests per month
    UNLIMITED = "unlimited"  # Enterprise tier with unlimited requests
