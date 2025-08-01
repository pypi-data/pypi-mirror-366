"""
Mock billing module for development.
"""
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class BillingPortalSession(BaseModel):
    """Mock billing portal session."""
    url: str = "https://billing.stripe.com/mock"
    id: str = "mock_session_id"

class StripeClient:
    """Mock Stripe client."""
    
    def __init__(self):
        logger.info("Mock Stripe client initialized")
    
    async def create_billing_portal_session(self, customer_id: str) -> BillingPortalSession:
        """Mock billing portal session creation."""
        return BillingPortalSession()
