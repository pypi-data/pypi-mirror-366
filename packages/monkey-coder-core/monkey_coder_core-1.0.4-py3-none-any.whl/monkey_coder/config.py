"""
Global configuration management for Monkey Coder Core.

This module handles environment-specific configurations including
data storage paths, ensuring proper use of mounted volumes in production.
"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StorageConfig:
    """
    Centralized storage configuration for the application.
    
    Handles data directory paths for different deployment environments,
    ensuring persistent data is stored in the appropriate location.
    """
    
    def __init__(self):
        """Initialize storage configuration based on environment."""
        # Check if we're running in Railway or production with /data volume
        if os.path.exists("/data") and os.access("/data", os.W_OK):
            self.data_dir = Path("/data")
            self.is_production = True
            logger.info("Using volume at /data for persistent storage")
        else:
            # Development mode - use local directory
            self.data_dir = Path.cwd() / "data"
            self.is_production = False
            logger.info(f"Using local directory {self.data_dir} for storage")
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Define subdirectories for different data types
        self.pricing_dir = self.data_dir / "pricing"
        self.mcp_dir = self.data_dir / "mcp"
        self.cache_dir = self.data_dir / "cache"
        self.uploads_dir = self.data_dir / "uploads"
        self.logs_dir = self.data_dir / "logs"
        
        # Create all subdirectories
        for directory in [self.pricing_dir, self.mcp_dir, self.cache_dir, 
                         self.uploads_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
    
    @property
    def pricing_data_file(self) -> Path:
        """Path to the pricing data JSON file."""
        return self.pricing_dir / "pricing_data.json"
    
    @property
    def mcp_config_file(self) -> Path:
        """Path to the MCP server configuration file."""
        return self.mcp_dir / "server_config.yaml"
    
    @property
    def mcp_state_file(self) -> Path:
        """Path to the MCP server state file."""
        return self.mcp_dir / "server_state.json"
    
    def get_upload_path(self, filename: str) -> Path:
        """
        Get path for uploaded files.
        
        Args:
            filename: Name of the file to upload
            
        Returns:
            Path: Full path where the file should be stored
        """
        return self.uploads_dir / filename
    
    def get_cache_path(self, cache_key: str) -> Path:
        """
        Get path for cached data.
        
        Args:
            cache_key: Unique key for the cached data
            
        Returns:
            Path: Full path for the cache file
        """
        return self.cache_dir / f"{cache_key}.cache"
    
    def get_log_path(self, log_name: str) -> Path:
        """
        Get path for log files.
        
        Args:
            log_name: Name of the log file
            
        Returns:
            Path: Full path for the log file
        """
        return self.logs_dir / log_name
    
    def cleanup_old_files(self, days: int = 30) -> None:
        """
        Clean up old files from storage directories.
        
        Args:
            days: Number of days to keep files
        """
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        # Clean cache and uploads directories
        for directory in [self.cache_dir, self.uploads_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            logger.info(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to delete {file_path}: {e}")


# Global storage configuration instance
storage_config = StorageConfig()


# Environment configuration
class Config:
    """Global application configuration."""
    
    # API Configuration
    API_HOST: str = os.getenv("HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # Storage
    STORAGE: StorageConfig = storage_config
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Provider API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Feature Flags
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_MCP: bool = os.getenv("ENABLE_MCP", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration and log warnings for missing values."""
        if not cls.JWT_SECRET_KEY:
            logger.warning("JWT_SECRET_KEY not set - using temporary key for development")
        
        if not cls.DATABASE_URL:
            logger.warning("DATABASE_URL not set - some features may be limited")
        
        if cls.STORAGE.is_production:
            logger.info("Running in production mode with /data volume")
        else:
            logger.info("Running in development mode with local storage")


# Create global config instance
config = Config()

# Validate on import
config.validate()
