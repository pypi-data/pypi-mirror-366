"""
Database connection management for PostgreSQL.

This module handles database connections and provides connection pooling
for the Monkey Coder Core API.
"""

import asyncio
import logging
import os
from typing import Optional

import asyncpg
from asyncpg import Pool

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[Pool] = None


async def get_database_connection() -> Pool:
    """
    Get or create the database connection pool.
    
    Returns:
        asyncpg.Pool: Database connection pool
        
    Raises:
        RuntimeError: If database connection fails
    """
    global _connection_pool
    
    if _connection_pool is None or _connection_pool.is_closing():
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        
        try:
            _connection_pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'jit': 'off'
                }
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise RuntimeError(f"Database connection failed: {e}")
    
    return _connection_pool


async def close_database_connection() -> None:
    """
    Close the database connection pool.
    """
    global _connection_pool
    
    if _connection_pool and not _connection_pool.is_closing():
        await _connection_pool.close()
        logger.info("Database connection pool closed")
        _connection_pool = None


async def test_database_connection() -> bool:
    """
    Test database connectivity.
    
    Returns:
        bool: True if connection is successful
    """
    try:
        pool = await get_database_connection()
        async with pool.acquire() as connection:
            result = await connection.fetchrow("SELECT 1 as test")
            return result["test"] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
