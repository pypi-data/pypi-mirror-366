"""
Mock database module for development.
"""
import logging

logger = logging.getLogger(__name__)

async def run_migrations():
    """Mock database migrations."""
    logger.info("Database migrations skipped for development")
    return True

async def get_database_connection():
    """Mock database connection."""
    logger.info("Database connection skipped for development")
    return None
