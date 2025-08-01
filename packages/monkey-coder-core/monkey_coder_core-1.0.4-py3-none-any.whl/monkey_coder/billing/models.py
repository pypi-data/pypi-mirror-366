"""
Billing models and data structures.

This module defines models for billing-related data structures
including portal sessions and billing information.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BillingPortalSession(BaseModel):
    """
    Model for billing portal session information.
    
    This represents a Stripe billing portal session that allows
    customers to manage their billing information and subscriptions.
    """
    session_url: str = Field(..., description="URL to the billing portal session")
    customer_id: str = Field(..., description="Stripe customer ID")
    expires_at: Optional[datetime] = Field(None, description="Session expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class BillingUsageReport(BaseModel):
    """
    Model for usage reporting to Stripe.
    
    This represents usage data that gets reported to Stripe
    for metered billing purposes.
    """
    api_key_hash: str = Field(..., description="Hashed API key identifier")
    period_start: datetime = Field(..., description="Start of reporting period")
    period_end: datetime = Field(..., description="End of reporting period")
    total_tokens: int = Field(..., description="Total tokens used in period")
    total_cost: float = Field(..., description="Total cost for the period")
    request_count: int = Field(..., description="Number of requests in period")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
