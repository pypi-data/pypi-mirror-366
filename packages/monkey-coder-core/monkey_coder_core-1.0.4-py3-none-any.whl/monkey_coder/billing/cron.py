"""
Cron job functions for billing operations.

This module contains functions designed to be run as scheduled jobs
for billing operations like reporting usage to Stripe.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ..database.models import UsageEvent, BillingCustomer
from .stripe_client import StripeClient

logger = logging.getLogger(__name__)


async def report_daily_usage_to_stripe() -> Dict[str, Any]:
    """
    Report daily usage to Stripe for all customers.
    
    This function is designed to be run as a daily cron job to report
    usage data to Stripe for metered billing. It aggregates usage data
    from the previous day and reports it to Stripe.
    
    Returns:
        Dict[str, Any]: Summary of reporting results
    """
    logger.info("Starting daily usage reporting to Stripe")
    
    # Calculate yesterday's date range
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    start_date = datetime.combine(yesterday, datetime.min.time())
    end_date = datetime.combine(yesterday, datetime.max.time())
    
    results = {
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "customers_processed": 0,
        "total_usage_reported": 0,
        "errors": [],
        "success": True
    }
    
    try:
        # Get all active billing customers
        # In a real implementation, you'd query the database for all customers
        # For now, we'll get unique API key hashes from usage events
        
        stripe_client = StripeClient()
        customers_processed = set()
        
        # Process usage in batches to avoid memory issues
        batch_size = 100
        offset = 0
        
        while True:
            # Get usage events for the day (batch processing)
            # This is a simplified approach - in production you'd want to
            # aggregate data more efficiently
            
            try:
                # Get unique API key hashes from usage events
                usage_events = await _get_usage_events_for_period(
                    start_date, end_date, limit=batch_size, offset=offset
                )
                
                if not usage_events:
                    break
                
                # Group usage by API key hash
                usage_by_customer = {}
                for event in usage_events:
                    api_key_hash = event.api_key_hash
                    if api_key_hash not in usage_by_customer:
                        usage_by_customer[api_key_hash] = {
                            "total_tokens": 0,
                            "total_cost": 0.0,
                            "request_count": 0,
                            "events": []
                        }
                    
                    usage_by_customer[api_key_hash]["total_tokens"] += event.tokens_total
                    usage_by_customer[api_key_hash]["total_cost"] += event.cost_total
                    usage_by_customer[api_key_hash]["request_count"] += 1
                    usage_by_customer[api_key_hash]["events"].append(event)
                
                # Report usage for each customer
                for api_key_hash, usage_data in usage_by_customer.items():
                    if api_key_hash in customers_processed:
                        continue
                    
                    try:
                        await _report_customer_usage_to_stripe(
                            stripe_client=stripe_client,
                            api_key_hash=api_key_hash,
                            usage_data=usage_data,
                            period_start=start_date,
                            period_end=end_date
                        )
                        
                        customers_processed.add(api_key_hash)
                        results["customers_processed"] += 1
                        results["total_usage_reported"] += usage_data["total_tokens"]
                        
                    except Exception as e:
                        error_msg = f"Failed to report usage for customer {api_key_hash}: {e}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                
                offset += batch_size
                
            except Exception as e:
                error_msg = f"Failed to process usage batch at offset {offset}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                break
        
        if results["errors"]:
            results["success"] = False
        
        logger.info(f"Daily usage reporting completed. Processed {results['customers_processed']} customers.")
        return results
        
    except Exception as e:
        error_msg = f"Fatal error in daily usage reporting: {e}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
        results["success"] = False
        return results


async def _get_usage_events_for_period(
    start_date: datetime,
    end_date: datetime,
    limit: int = 100,
    offset: int = 0
) -> List[UsageEvent]:
    """
    Get usage events for a specific period.
    
    Args:
        start_date: Start of period
        end_date: End of period
        limit: Maximum events to return
        offset: Offset for pagination
        
    Returns:
        List[UsageEvent]: Usage events
    """
    # This is a simplified implementation
    # In production, you'd want to optimize this query
    
    from ..database.connection import get_database_connection
    import json
    
    pool = await get_database_connection()
    async with pool.acquire() as connection:
        query = """
            SELECT * FROM usage_events
            WHERE created_at >= $1 AND created_at <= $2
            ORDER BY created_at
            LIMIT $3 OFFSET $4
        """
        
        rows = await connection.fetch(query, start_date, end_date, limit, offset)
        
        events = []
        for row in rows:
            event_data = dict(row)
            if event_data.get('metadata'):
                event_data['metadata'] = json.loads(event_data['metadata'])
            else:
                event_data['metadata'] = {}
            events.append(UsageEvent(**event_data))
        
        return events


async def _report_customer_usage_to_stripe(
    stripe_client: StripeClient,
    api_key_hash: str,
    usage_data: Dict[str, Any],
    period_start: datetime,
    period_end: datetime
) -> None:
    """
    Report usage for a specific customer to Stripe.
    
    Args:
        stripe_client: Stripe client instance
        api_key_hash: Customer's hashed API key
        usage_data: Aggregated usage data
        period_start: Start of reporting period
        period_end: End of reporting period
    """
    try:
        # Get billing customer information
        billing_customer = await BillingCustomer.get_by_api_key_hash(api_key_hash)
        if not billing_customer:
            logger.warning(f"No billing customer found for API key hash: {api_key_hash}")
            return
        
        # In a real implementation, you would:
        # 1. Get the customer's Stripe subscription
        # 2. Find the appropriate subscription item for usage-based billing
        # 3. Report the usage to that subscription item
        
        # For this example, we'll assume you have a subscription item ID
        # In practice, you'd store this in your billing_customers table
        # or fetch it from Stripe using the customer ID
        
        # Example of reporting usage (this would need real subscription item IDs):
        # stripe_client.report_usage(
        #     subscription_item_id="si_example123", 
        #     quantity=usage_data["total_tokens"]
        # )
        
        logger.info(
            f"Would report {usage_data['total_tokens']} tokens "
            f"(${usage_data['total_cost']:.6f}) for customer {billing_customer.stripe_customer_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to report usage for customer {api_key_hash}: {e}")
        raise


# Additional utility functions for cron jobs

async def cleanup_old_usage_events(days_to_keep: int = 90) -> Dict[str, Any]:
    """
    Clean up old usage events to manage database size.
    
    Args:
        days_to_keep: Number of days of usage events to keep
        
    Returns:
        Dict[str, Any]: Cleanup results
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    from ..database.connection import get_database_connection
    
    pool = await get_database_connection()
    async with pool.acquire() as connection:
        # Count events to be deleted
        count_result = await connection.fetchrow("""
            SELECT COUNT(*) as count FROM usage_events WHERE created_at < $1
        """, cutoff_date)
        
        events_to_delete = count_result["count"]
        
        # Delete old events
        await connection.execute("""
            DELETE FROM usage_events WHERE created_at < $1
        """, cutoff_date)
        
        logger.info(f"Cleaned up {events_to_delete} usage events older than {days_to_keep} days")
        
        return {
            "cutoff_date": cutoff_date.isoformat(),
            "events_deleted": events_to_delete,
            "success": True
        }
