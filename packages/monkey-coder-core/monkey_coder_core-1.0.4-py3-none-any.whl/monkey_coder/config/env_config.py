"""
Environment Configuration Module

Centralized environment variable management with type safety and validation.
Addresses the dotenv injection issue with proper configuration management.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration with defaults."""
    url: Optional[str] = None
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass 
class AIProviderConfig:
    """AI provider configuration."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    mfa_enabled: bool = False
    mfa_issuer: str = "Monkey Coder"


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    log_level: str = "info"


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True
    enable_tracing: bool = False
    log_level: str = "INFO"


class EnvironmentConfig:
    """
    Centralized environment configuration manager.
    
    Provides type-safe access to environment variables with validation,
    defaults, and proper error handling.
    """
    
    def __init__(self, env_file: Optional[Union[str, Path]] = None):
        """
        Initialize environment configuration.
        
        Args:
            env_file: Optional path to .env file to load
        """
        self._env_loaded = False
        self._config_cache: Dict[str, Any] = {}
        
        # Load environment file if specified
        if env_file:
            self._load_env_file(env_file)
        
        # Initialize configuration sections
        self.database = self._init_database_config()
        self.ai_providers = self._init_ai_provider_config()
        self.security = self._init_security_config()
        self.server = self._init_server_config()
        self.monitoring = self._init_monitoring_config()
        
        # Set environment flag
        self.environment = self._get_env("ENVIRONMENT", "development")
        self.debug = self._get_env_bool("DEBUG", self.environment == "development")
        
        logger.info(f"Environment configuration loaded: {self.environment}")
    
    def _load_env_file(self, env_file: Union[str, Path]) -> None:
        """Load environment variables from file."""
        try:
            from dotenv import load_dotenv
            
            env_path = Path(env_file)
            if env_path.exists():
                load_dotenv(env_path, override=True)
                self._env_loaded = True
                logger.info(f"Loaded environment from: {env_path}")
            else:
                logger.warning(f"Environment file not found: {env_path}")
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env file loading")
        except Exception as e:
            logger.error(f"Failed to load environment file: {e}")
    
    def _get_env(self, key: str, default: Any = None) -> Any:
        """Get environment variable with caching."""
        if key in self._config_cache:
            return self._config_cache[key]
        
        value = os.getenv(key, default)
        self._config_cache[key] = value
        return value
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = self._get_env(key, str(default).lower())
        return str(value).lower() in ('true', '1', 'yes', 'on')
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer environment variable."""
        try:
            return int(self._get_env(key, default))
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def _init_database_config(self) -> DatabaseConfig:
        """Initialize database configuration."""
        return DatabaseConfig(
            url=self._get_env("DATABASE_URL"),
            pool_size=self._get_env_int("DB_POOL_SIZE", 10),
            pool_timeout=self._get_env_int("DB_POOL_TIMEOUT", 30),
            pool_recycle=self._get_env_int("DB_POOL_RECYCLE", 3600),
            echo=self._get_env_bool("DB_ECHO", False)
        )
    
    def _init_ai_provider_config(self) -> AIProviderConfig:
        """Initialize AI provider configuration."""
        return AIProviderConfig(
            openai_api_key=self._get_env("OPENAI_API_KEY"),
            anthropic_api_key=self._get_env("ANTHROPIC_API_KEY"),
            google_api_key=self._get_env("GOOGLE_API_KEY"),
            groq_api_key=self._get_env("GROQ_API_KEY"),
            grok_api_key=self._get_env("GROK_API_KEY")
        )
    
    def _init_security_config(self) -> SecurityConfig:
        """Initialize security configuration."""
        return SecurityConfig(
            jwt_secret_key=self._get_env("JWT_SECRET_KEY"),
            jwt_algorithm=self._get_env("JWT_ALGORITHM", "HS256"),
            jwt_access_token_expire_minutes=self._get_env_int("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30),
            jwt_refresh_token_expire_days=self._get_env_int("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7),
            mfa_enabled=self._get_env_bool("MFA_ENABLED", False),
            mfa_issuer=self._get_env("MFA_ISSUER", "Monkey Coder")
        )
    
    def _init_server_config(self) -> ServerConfig:
        """Initialize server configuration."""
        return ServerConfig(
            host=self._get_env("HOST", "0.0.0.0"),
            port=self._get_env_int("PORT", 8000),
            reload=self._get_env_bool("RELOAD", False),
            workers=self._get_env_int("WORKERS", 1),
            log_level=self._get_env("LOG_LEVEL", "info")
        )
    
    def _init_monitoring_config(self) -> MonitoringConfig:
        """Initialize monitoring configuration."""
        return MonitoringConfig(
            sentry_dsn=self._get_env("SENTRY_DSN"),
            enable_metrics=self._get_env_bool("ENABLE_METRICS", True),
            enable_tracing=self._get_env_bool("ENABLE_TRACING", False),
            log_level=self._get_env("LOG_LEVEL", "INFO")
        )
    
    def validate_required_config(self) -> Dict[str, list]:
        """
        Validate required configuration and return any missing values.
        
        Returns:
            Dict with 'missing' and 'warnings' lists
        """
        missing = []
        warnings = []
        
        # Check AI provider keys (at least one required)
        ai_keys = [
            self.ai_providers.openai_api_key,
            self.ai_providers.anthropic_api_key,
            self.ai_providers.google_api_key,
            self.ai_providers.groq_api_key,
            self.ai_providers.grok_api_key
        ]
        
        if not any(ai_keys):
            missing.append("At least one AI provider API key required")
        
        # Check security config for production
        if self.environment == "production":
            if not self.security.jwt_secret_key:
                missing.append("JWT_SECRET_KEY required for production")
            
            if not self.monitoring.sentry_dsn:
                warnings.append("SENTRY_DSN recommended for production monitoring")
        
        return {
            "missing": missing,
            "warnings": warnings
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging (without sensitive values)."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "workers": self.server.workers
            },
            "database": {
                "configured": bool(self.database.url),
                "pool_size": self.database.pool_size
            },
            "ai_providers": {
                "openai": bool(self.ai_providers.openai_api_key),
                "anthropic": bool(self.ai_providers.anthropic_api_key),
                "google": bool(self.ai_providers.google_api_key),
                "groq": bool(self.ai_providers.groq_api_key),
                "grok": bool(self.ai_providers.grok_api_key)
            },
            "security": {
                "jwt_configured": bool(self.security.jwt_secret_key),
                "mfa_enabled": self.security.mfa_enabled
            },
            "monitoring": {
                "sentry_configured": bool(self.monitoring.sentry_dsn),
                "metrics_enabled": self.monitoring.enable_metrics
            }
        }


# Global configuration instance
_config_instance: Optional[EnvironmentConfig] = None


def get_config(env_file: Optional[Union[str, Path]] = None, reload: bool = False) -> EnvironmentConfig:
    """
    Get global configuration instance.
    
    Args:
        env_file: Optional path to environment file
        reload: Force reload of configuration
        
    Returns:
        EnvironmentConfig instance
    """
    global _config_instance
    
    if _config_instance is None or reload:
        _config_instance = EnvironmentConfig(env_file)
    
    return _config_instance


# Convenience functions for common config access
def get_database_url() -> Optional[str]:
    """Get database URL."""
    return get_config().database.url


def get_ai_provider_keys() -> Dict[str, Optional[str]]:
    """Get all AI provider API keys."""
    config = get_config()
    return {
        "openai": config.ai_providers.openai_api_key,
        "anthropic": config.ai_providers.anthropic_api_key,
        "google": config.ai_providers.google_api_key,
        "groq": config.ai_providers.groq_api_key,
        "grok": config.ai_providers.grok_api_key
    }


def is_production() -> bool:
    """Check if running in production environment."""
    return get_config().environment == "production"


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return get_config().debug