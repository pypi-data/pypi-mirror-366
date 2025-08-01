"""
Database migrations for usage tracking and billing.

This module contains database schema migrations to create and update
the required tables for usage metering and billing functionality.
"""

import logging
from typing import List

from .connection import get_database_connection

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class."""
    
    def __init__(self, version: str, description: str, sql: str):
        self.version = version
        self.description = description
        self.sql = sql


# Migration definitions
MIGRATIONS = {
    "001_create_usage_events_table": Migration(
        version="001",
        description="Create usage_events table for tracking API usage",
        sql="""
            CREATE TABLE IF NOT EXISTS usage_events (
                id VARCHAR(36) PRIMARY KEY,
                api_key_hash VARCHAR(64) NOT NULL,
                execution_id VARCHAR(36) NOT NULL,
                task_type VARCHAR(50) NOT NULL,
                
                -- Token usage
                tokens_input INTEGER NOT NULL DEFAULT 0,
                tokens_output INTEGER NOT NULL DEFAULT 0,
                tokens_total INTEGER NOT NULL DEFAULT 0,
                
                -- Provider and model info
                provider VARCHAR(50) NOT NULL,
                model VARCHAR(100) NOT NULL,
                model_cost_input DECIMAL(12, 8) NOT NULL DEFAULT 0.0,
                model_cost_output DECIMAL(12, 8) NOT NULL DEFAULT 0.0,
                
                -- Calculated costs
                cost_input DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
                cost_output DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
                cost_total DECIMAL(10, 6) NOT NULL DEFAULT 0.0,
                
                -- Execution metadata
                execution_time DECIMAL(8, 3) NOT NULL DEFAULT 0.0,
                status VARCHAR(20) NOT NULL DEFAULT 'completed',
                error_message TEXT,
                
                -- Timestamps
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                
                -- Additional metadata as JSON
                metadata JSONB
            );
            
            -- Create indexes for efficient queries
            CREATE INDEX IF NOT EXISTS idx_usage_events_api_key_hash ON usage_events(api_key_hash);
            CREATE INDEX IF NOT EXISTS idx_usage_events_created_at ON usage_events(created_at);
            CREATE INDEX IF NOT EXISTS idx_usage_events_provider ON usage_events(provider);
            CREATE INDEX IF NOT EXISTS idx_usage_events_model ON usage_events(model);
            CREATE INDEX IF NOT EXISTS idx_usage_events_status ON usage_events(status);
            CREATE INDEX IF NOT EXISTS idx_usage_events_api_key_created ON usage_events(api_key_hash, created_at);
        """
    ),
    
    "002_create_billing_customers_table": Migration(
        version="002", 
        description="Create billing_customers table for Stripe integration",
        sql="""
            CREATE TABLE IF NOT EXISTS billing_customers (
                id VARCHAR(36) PRIMARY KEY,
                api_key_hash VARCHAR(64) NOT NULL UNIQUE,
                stripe_customer_id VARCHAR(100) NOT NULL UNIQUE,
                
                -- Customer metadata
                email VARCHAR(255),
                name VARCHAR(255),
                company VARCHAR(255),
                
                -- Billing settings
                billing_interval VARCHAR(20) NOT NULL DEFAULT 'monthly',
                is_active BOOLEAN NOT NULL DEFAULT true,
                
                -- Timestamps
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_billing_customers_api_key_hash ON billing_customers(api_key_hash);
            CREATE INDEX IF NOT EXISTS idx_billing_customers_stripe_id ON billing_customers(stripe_customer_id);
            CREATE INDEX IF NOT EXISTS idx_billing_customers_active ON billing_customers(is_active);
        """
    ),
    
    "003_create_migrations_table": Migration(
        version="003",
        description="Create migrations tracking table",
        sql="""
            CREATE TABLE IF NOT EXISTS migrations (
                version VARCHAR(10) PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """
    ),
    
    "004_create_users_table": Migration(
        version="004",
        description="Create users table for authentication and account management",
        sql="""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                
                -- User metadata
                full_name VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT true,
                is_verified BOOLEAN NOT NULL DEFAULT false,
                
                -- Roles and permissions
                roles JSONB NOT NULL DEFAULT '[]',
                is_developer BOOLEAN NOT NULL DEFAULT false,
                
                -- Subscription and billing
                subscription_plan VARCHAR(50) NOT NULL DEFAULT 'hobby',
                api_key_hash VARCHAR(64),
                
                -- Timestamps
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                last_login TIMESTAMP WITH TIME ZONE,
                
                -- Additional metadata as JSON
                metadata JSONB NOT NULL DEFAULT '{}'
            );
            
            -- Create indexes for efficient queries
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
            CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_plan);
            CREATE INDEX IF NOT EXISTS idx_users_api_key_hash ON users(api_key_hash);
            CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
        """
    )
}


async def run_migrations() -> None:
    """
    Run all pending database migrations.
    
    This function checks which migrations have been applied and runs
    any pending migrations in order.
    """
    pool = await get_database_connection()
    async with pool.acquire() as connection:
        # First, create the migrations table if it doesn't exist
        await connection.execute(MIGRATIONS["003_create_migrations_table"].sql)
        
        # Get list of applied migrations
        applied_migrations = await connection.fetch("""
            SELECT version FROM migrations ORDER BY version
        """)
        applied_versions = {row["version"] for row in applied_migrations}
        
        # Run pending migrations in order
        migration_keys = sorted([k for k in MIGRATIONS.keys() if k != "003_create_migrations_table"])
        
        for migration_key in migration_keys:
            migration = MIGRATIONS[migration_key]
            
            if migration.version not in applied_versions:
                logger.info(f"Running migration {migration.version}: {migration.description}")
                
                try:
                    # Execute migration
                    await connection.execute(migration.sql)
                    
                    # Record migration as applied
                    await connection.execute("""
                        INSERT INTO migrations (version, description) VALUES ($1, $2)
                    """, migration.version, migration.description)
                    
                    logger.info(f"Migration {migration.version} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Migration {migration.version} failed: {e}")
                    raise
            else:
                logger.debug(f"Migration {migration.version} already applied")
        
        logger.info("All migrations completed successfully")


async def check_migration_status() -> List[dict]:
    """
    Check the status of all migrations.
    
    Returns:
        List[dict]: List of migration statuses
    """
    pool = await get_database_connection()
    async with pool.acquire() as connection:
        # Ensure migrations table exists
        await connection.execute(MIGRATIONS["003_create_migrations_table"].sql)
        
        # Get applied migrations  
        applied_migrations = await connection.fetch("""
            SELECT version, description, applied_at FROM migrations ORDER BY version
        """)
        applied_versions = {row["version"]: row for row in applied_migrations}
        
        # Build status for all migrations
        status = []
        migration_keys = sorted([k for k in MIGRATIONS.keys() if k != "003_create_migrations_table"])
        
        for migration_key in migration_keys:
            migration = MIGRATIONS[migration_key]
            
            if migration.version in applied_versions:
                applied_info = applied_versions[migration.version]
                status.append({
                    "version": migration.version,
                    "description": migration.description, 
                    "status": "applied",
                    "applied_at": applied_info["applied_at"]
                })
            else:
                status.append({
                    "version": migration.version,
                    "description": migration.description,
                    "status": "pending",
                    "applied_at": None
                })
        
        return status
