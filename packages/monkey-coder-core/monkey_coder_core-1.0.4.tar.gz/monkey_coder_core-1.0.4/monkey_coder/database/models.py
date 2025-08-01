"""
Database models for usage tracking and billing.

This module defines the database models for storing usage events,
billing information, and related data.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, Field

from .connection import get_database_connection

logger = logging.getLogger(__name__)


class UsageEvent(BaseModel):
    """
    Model for tracking API usage events.
    
    This model stores detailed information about each API request
    for billing and analytics purposes.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    api_key_hash: str = Field(..., description="Hashed API key identifier")
    execution_id: str = Field(..., description="Execution identifier from task")
    task_type: str = Field(..., description="Type of task executed")
    
    # Usage metrics
    tokens_input: int = Field(..., description="Input tokens consumed")
    tokens_output: int = Field(..., description="Output tokens generated")
    tokens_total: int = Field(..., description="Total tokens used")
    
    # Provider and model information
    provider: str = Field(..., description="AI provider used")
    model: str = Field(..., description="Model used for execution")
    model_cost_input: float = Field(..., description="Cost per input token")
    model_cost_output: float = Field(..., description="Cost per output token")
    
    # Calculated costs
    cost_input: float = Field(..., description="Input cost (tokens × price)")
    cost_output: float = Field(..., description="Output cost (tokens × price)")
    cost_total: float = Field(..., description="Total cost for this event")
    
    # Execution metadata
    execution_time: float = Field(..., description="Execution time in seconds")
    status: str = Field(..., description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }

    @classmethod
    async def create(cls, **kwargs) -> "UsageEvent":
        """
        Create a new usage event in the database.
        
        Args:
            **kwargs: Usage event data
            
        Returns:
            UsageEvent: Created usage event
        """
        event = cls(**kwargs)
        
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO usage_events (
                    id, api_key_hash, execution_id, task_type,
                    tokens_input, tokens_output, tokens_total,
                    provider, model, model_cost_input, model_cost_output,
                    cost_input, cost_output, cost_total,
                    execution_time, status, error_message,
                    created_at, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
                )
            """,
                event.id, event.api_key_hash, event.execution_id, event.task_type,
                event.tokens_input, event.tokens_output, event.tokens_total,
                event.provider, event.model, event.model_cost_input, event.model_cost_output,
                event.cost_input, event.cost_output, event.cost_total,
                event.execution_time, event.status, event.error_message,
                event.created_at, json.dumps(event.metadata)
            )
        
        logger.info(f"Created usage event: {event.id}")
        return event
    
    @classmethod
    async def get_usage_by_api_key(
        cls,
        api_key_hash: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List["UsageEvent"]:
        """
        Get usage events for an API key.
        
        Args:
            api_key_hash: Hashed API key
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of events to return
            
        Returns:
            List[UsageEvent]: List of usage events
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            query = """
                SELECT * FROM usage_events
                WHERE api_key_hash = $1
            """
            params = [api_key_hash]
            
            if start_date:
                query += " AND created_at >= $2"
                params.append(start_date)
                
                if end_date:
                    query += " AND created_at <= $3"
                    params.append(end_date)
            elif end_date:
                query += " AND created_at <= $2"
                params.append(end_date)
            
            query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            rows = await connection.fetch(query, *params)
            
            events = []
            for row in rows:
                event_data = dict(row)
                if event_data.get('metadata'):
                    event_data['metadata'] = json.loads(event_data['metadata'])
                else:
                    event_data['metadata'] = {}
                events.append(cls(**event_data))
            
            return events
    
    @classmethod
    async def get_usage_summary(
        cls,
        api_key_hash: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get usage summary for an API key.
        
        Args:
            api_key_hash: Hashed API key
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict: Usage summary statistics
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            query = """
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(tokens_total) as total_tokens,
                    SUM(cost_total) as total_cost,
                    AVG(execution_time) as avg_execution_time,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_requests,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_requests
                FROM usage_events
                WHERE api_key_hash = $1
            """
            params = [api_key_hash]
            
            if start_date:
                query += " AND created_at >= $2"
                params.append(start_date)
                
                if end_date:
                    query += " AND created_at <= $3"
                    params.append(end_date)
            elif end_date:
                query += " AND created_at <= $2"
                params.append(end_date)
            
            row = await connection.fetchrow(query, *params)
            
            return {
                "total_requests": row["total_requests"] or 0,
                "total_tokens": row["total_tokens"] or 0,
                "total_cost": float(row["total_cost"] or 0),
                "avg_execution_time": float(row["avg_execution_time"] or 0),
                "successful_requests": row["successful_requests"] or 0,
                "failed_requests": row["failed_requests"] or 0,
                "success_rate": (row["successful_requests"] / row["total_requests"]) if row["total_requests"] > 0 else 0,
            }


class BillingCustomer(BaseModel):
    """
    Model for storing billing customer information.
    
    This model links API keys to Stripe customers for billing.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    api_key_hash: str = Field(..., description="Hashed API key identifier")
    stripe_customer_id: str = Field(..., description="Stripe customer ID")
    
    # Customer metadata
    email: Optional[str] = Field(None, description="Customer email")
    name: Optional[str] = Field(None, description="Customer name")
    company: Optional[str] = Field(None, description="Customer company")
    
    # Billing settings
    billing_interval: str = Field(default="monthly", description="Billing interval")
    is_active: bool = Field(default=True, description="Whether customer is active")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }

    @classmethod
    async def create(cls, **kwargs) -> "BillingCustomer":
        """
        Create a new billing customer in the database.
        
        Args:
            **kwargs: Customer data
            
        Returns:
            BillingCustomer: Created customer
        """
        customer = cls(**kwargs)
        
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO billing_customers (
                    id, api_key_hash, stripe_customer_id,
                    email, name, company,
                    billing_interval, is_active,
                    created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
                )
            """,
                customer.id, customer.api_key_hash, customer.stripe_customer_id,
                customer.email, customer.name, customer.company,
                customer.billing_interval, customer.is_active,
                customer.created_at, customer.updated_at
            )
        
        logger.info(f"Created billing customer: {customer.id}")
        return customer
    
    @classmethod
    async def get_by_api_key_hash(cls, api_key_hash: str) -> Optional["BillingCustomer"]:
        """
        Get billing customer by API key hash.
        
        Args:
            api_key_hash: Hashed API key
            
        Returns:
            Optional[BillingCustomer]: Customer if found
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            row = await connection.fetchrow("""
                SELECT * FROM billing_customers
                WHERE api_key_hash = $1 AND is_active = true
            """, api_key_hash)
            
            if row:
                return cls(**dict(row))
            return None
    
    @classmethod
    async def get_by_stripe_customer_id(cls, stripe_customer_id: str) -> Optional["BillingCustomer"]:
        """
        Get billing customer by Stripe customer ID.
        
        Args:
            stripe_customer_id: Stripe customer ID
            
        Returns:
            Optional[BillingCustomer]: Customer if found
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            row = await connection.fetchrow("""
                SELECT * FROM billing_customers
                WHERE stripe_customer_id = $1 AND is_active = true
            """, stripe_customer_id)
            
            if row:
                return cls(**dict(row))
            return None


class User(BaseModel):
    """
    Model for user accounts and authentication.
    
    This model stores user information for authentication and account management.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email address")
    password_hash: str = Field(..., description="Hashed password")
    
    # User metadata
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(default=True, description="Whether user account is active")
    is_verified: bool = Field(default=False, description="Whether email is verified")
    
    # Roles and permissions
    roles: List[str] = Field(default_factory=list, description="User roles")
    is_developer: bool = Field(default=False, description="Whether user has developer access")
    
    # Subscription and billing
    subscription_plan: str = Field(default="hobby", description="User's subscription plan")
    api_key_hash: Optional[str] = Field(None, description="Associated API key hash")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }

    @classmethod
    async def create(cls, **kwargs) -> "User":
        """
        Create a new user in the database.
        
        Args:
            **kwargs: User data
            
        Returns:
            User: Created user
        """
        user = cls(**kwargs)
        
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO users (
                    id, username, email, password_hash,
                    full_name, is_active, is_verified,
                    roles, is_developer, subscription_plan, api_key_hash,
                    created_at, updated_at, last_login, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                )
            """,
                user.id, user.username, user.email, user.password_hash,
                user.full_name, user.is_active, user.is_verified,
                json.dumps(user.roles), user.is_developer, user.subscription_plan, user.api_key_hash,
                user.created_at, user.updated_at, user.last_login, json.dumps(user.metadata)
            )
        
        logger.info(f"Created user: {user.id} ({user.email})")
        return user
    
    @classmethod
    async def get_by_id(cls, user_id: str) -> Optional["User"]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User if found
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            row = await connection.fetchrow("""
                SELECT * FROM users WHERE id = $1 AND is_active = true
            """, user_id)
            
            if row:
                user_data = dict(row)
                if user_data.get('roles'):
                    user_data['roles'] = json.loads(user_data['roles'])
                else:
                    user_data['roles'] = []
                if user_data.get('metadata'):
                    user_data['metadata'] = json.loads(user_data['metadata'])
                else:
                    user_data['metadata'] = {}
                return cls(**user_data)
            return None
    
    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            Optional[User]: User if found
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            row = await connection.fetchrow("""
                SELECT * FROM users WHERE email = $1 AND is_active = true
            """, email.lower())
            
            if row:
                user_data = dict(row)
                if user_data.get('roles'):
                    user_data['roles'] = json.loads(user_data['roles'])
                else:
                    user_data['roles'] = []
                if user_data.get('metadata'):
                    user_data['metadata'] = json.loads(user_data['metadata'])
                else:
                    user_data['metadata'] = {}
                return cls(**user_data)
            return None
    
    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            Optional[User]: User if found
        """
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            row = await connection.fetchrow("""
                SELECT * FROM users WHERE username = $1 AND is_active = true
            """, username)
            
            if row:
                user_data = dict(row)
                if user_data.get('roles'):
                    user_data['roles'] = json.loads(user_data['roles'])
                else:
                    user_data['roles'] = []
                if user_data.get('metadata'):
                    user_data['metadata'] = json.loads(user_data['metadata'])
                else:
                    user_data['metadata'] = {}
                return cls(**user_data)
            return None
    
    async def update_last_login(self) -> None:
        """Update the user's last login timestamp."""
        self.last_login = datetime.utcnow()
        
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            await connection.execute("""
                UPDATE users SET last_login = $1, updated_at = $2 WHERE id = $3
            """, self.last_login, datetime.utcnow(), self.id)
    
    async def update(self, **kwargs) -> None:
        """
        Update user fields.
        
        Args:
            **kwargs: Fields to update
        """
        # Update local fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            await connection.execute("""
                UPDATE users SET 
                    username = $1, email = $2, password_hash = $3,
                    full_name = $4, is_active = $5, is_verified = $6,
                    roles = $7, is_developer = $8, subscription_plan = $9, api_key_hash = $10,
                    updated_at = $11, last_login = $12, metadata = $13
                WHERE id = $14
            """,
                self.username, self.email, self.password_hash,
                self.full_name, self.is_active, self.is_verified,
                json.dumps(self.roles), self.is_developer, self.subscription_plan, self.api_key_hash,
                self.updated_at, self.last_login, json.dumps(self.metadata),
                self.id
            )
