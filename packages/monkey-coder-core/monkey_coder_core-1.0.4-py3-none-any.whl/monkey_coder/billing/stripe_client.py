"""
Stripe client and utility functions.

This module provides a Stripe client for interacting with the Stripe API,
including creating customers, processing invoices, and reporting usage.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import stripe

logger = logging.getLogger(__name__)


class StripeClient:
    """
    Client for interacting with the Stripe API.
    
    This class provides methods for managing customers, processing
    invoices, reporting usage, and other Stripe operations.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        stripe.api_key = self.api_key
        self.stripe = stripe
    
    def create_customer(self, email: str, name: str, api_key_hash: str) -> str:
        """
        Create a new customer on Stripe.
        
        Args:
            email: Customer email address
            name: Customer name
            api_key_hash: Hashed API key
            
        Returns:
            str: Stripe customer ID
        """
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata={"api_key_hash": api_key_hash}
            )
            
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
        
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    def create_billing_portal_session(self, customer_id: str, return_url: str) -> str:
        """
        Create a billing portal session for a customer.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to redirect to after session
            
        Returns:
            str: URL to the billing portal session
        """
        try:
            session = self.stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            logger.info(f"Created billing portal session for customer: {customer_id}")
            return session.url
        
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise
    
    def report_usage(self, subscription_item_id: str, quantity: int) -> Dict:
        """
        Report usage for a metered billing subscription item.
        
        Args:
            subscription_item_id: Stripe subscription item ID
            quantity: Usage quantity to report
            
        Returns:
            Dict: Usage record as returned by Stripe
        """
        try:
            usage_record = self.stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp="now",
                action="increment"
            )
            
            logger.info(f"Reported usage for subscription item {subscription_item_id}: {quantity}")
            return usage_record
        
        except stripe.error.StripeError as e:
            logger.error(f"Failed to report usage: {e}")
            raise


# Functions


def create_stripe_customer(email: str, name: str, api_key_hash: str) -> str:
    """
    Create a Stripe customer using the StripeClient.
    
    Args:
        email: Customer email
        name: Customer name
        api_key_hash: Hashed API key
        
    Returns:
        str: Stripe customer ID
    """
    client = StripeClient()
    return client.create_customer(email, name, api_key_hash)


def report_usage_to_stripe(subscription_item_id: str, quantity: int) -> Dict:
    """
    Report usage to Stripe using the StripeClient.
    
    Args:
        subscription_item_id: Stripe subscription item ID
        quantity: Usage quantity
        
    Returns:
        Dict: Usage record
    """
    client = StripeClient()
    return client.report_usage(subscription_item_id, quantity)

