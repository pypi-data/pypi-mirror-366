"""
Sentry configuration for Monkey Coder Core and CLI error tracking.

This module provides centralized Sentry configuration for both backend and CLI
components with proper error filtering, performance monitoring, and context.
"""

import os
import logging
from typing import Dict, Any, Optional
import sentry_sdk
# Skip problematic imports for development
try:
    from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration
except (ImportError, Exception):
    SqlAlchemyIntegration = None
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def configure_sentry(
    component: str = "core",
    environment: str = None,
    debug: bool = False,
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1
) -> None:
    """
    Configure Sentry SDK for error tracking and performance monitoring.
    
    Args:
        component: Component name (core, cli)
        environment: Environment name (production, staging, development)
        debug: Enable debug mode
        sample_rate: Error sampling rate (0.0 to 1.0)
        traces_sample_rate: Performance monitoring sampling rate
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logger.warning("SENTRY_DSN not configured, Sentry disabled")
        return
    
    # Determine environment
    if not environment:
        environment = os.getenv("ENVIRONMENT", "development")
    
    # Configure integrations based on component
    integrations = [
        LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        ),
        AsyncioIntegration(),
    ]
    
    if component == "core":
        integrations.append(FastApiIntegration())
        if SqlAlchemyIntegration:
            integrations.append(SqlAlchemyIntegration())
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=integrations,
        traces_sample_rate=traces_sample_rate,
        sample_rate=sample_rate,
        debug=debug,
        release=f"monkey-coder-{component}@1.0.0",
        before_send=_before_send_filter,
        before_send_transaction=_before_send_transaction_filter,
        attach_stacktrace=True,
        send_default_pii=False,  # Don't send personally identifiable information
    )
    
    # Set component context
    sentry_sdk.set_tag("component", component)
    sentry_sdk.set_tag("version", "1.0.0")
    
    logger.info(f"Sentry configured for {component} in {environment} environment")


def _before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter Sentry events before sending.
    
    Args:
        event: Sentry event data
        hint: Additional context
        
    Returns:
        Modified event or None to drop
    """
    # Don't send events for certain exceptions
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Filter out common/expected exceptions
        if exc_type.__name__ in [
            'KeyboardInterrupt',
            'SystemExit',
            'BrokenPipeError',
        ]:
            return None
        
        # Filter out HTTP client errors (4xx) unless they're auth errors
        if hasattr(exc_value, 'status_code'):
            status_code = getattr(exc_value, 'status_code', 0)
            if 400 <= status_code < 500 and status_code not in [401, 403]:
                return None
    
    # Sanitize sensitive data
    if 'request' in event:
        request = event['request']
        
        # Remove API keys from headers
        if 'headers' in request:
            headers = request['headers']
            for key in list(headers.keys()):
                if key.lower() in ['authorization', 'x-api-key', 'api-key']:
                    headers[key] = '[Filtered]'
        
        # Remove sensitive query parameters
        if 'query_string' in request:
            # Replace with sanitized version
            request['query_string'] = '[Filtered]'
    
    return event


def _before_send_transaction_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter Sentry performance transactions before sending.
    
    Args:
        event: Transaction event data
        hint: Additional context
        
    Returns:
        Modified event or None to drop
    """
    # Don't send transactions for health checks
    if event.get('transaction') in ['/health', '/metrics']:
        return None
    
    return event


def capture_exception_with_context(
    exception: Exception,
    context: Dict[str, Any] = None,
    tags: Dict[str, str] = None,
    level: str = "error"
) -> str:
    """
    Capture exception with additional context.
    
    Args:
        exception: Exception to capture
        context: Additional context data
        tags: Tags to add to the event
        level: Error level (error, warning, info)
        
    Returns:
        Sentry event ID
    """
    with sentry_sdk.push_scope() as scope:
        # Add context
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        # Add tags
        if tags:
            for key, value in tags.items():
                scope.set_tag(key, value)
        
        scope.level = level
        
        return sentry_sdk.capture_exception(exception)


def capture_message_with_context(
    message: str,
    context: Dict[str, Any] = None,
    tags: Dict[str, str] = None,
    level: str = "info"
) -> str:
    """
    Capture message with additional context.
    
    Args:
        message: Message to capture
        context: Additional context data
        tags: Tags to add to the event
        level: Message level (error, warning, info)
        
    Returns:
        Sentry event ID
    """
    with sentry_sdk.push_scope() as scope:
        # Add context
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        # Add tags
        if tags:
            for key, value in tags.items():
                scope.set_tag(key, value)
        
        scope.level = level
        
        return sentry_sdk.capture_message(message)


def set_user_context(user_id: str, api_key_hash: str = None) -> None:
    """
    Set user context for Sentry events.
    
    Args:
        user_id: User identifier
        api_key_hash: Hashed API key for context
    """
    sentry_sdk.set_user({
        "id": user_id,
        "api_key_hash": api_key_hash
    })


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: Dict[str, Any] = None) -> None:
    """
    Add breadcrumb for debugging context.
    
    Args:
        message: Breadcrumb message
        category: Category of breadcrumb
        level: Level of breadcrumb
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


# CLI-specific Sentry configuration
def configure_cli_sentry(debug: bool = False) -> None:
    """Configure Sentry specifically for CLI component."""
    configure_sentry(
        component="cli",
        debug=debug,
        sample_rate=0.8,  # Lower sample rate for CLI
        traces_sample_rate=0.05  # Very low for CLI performance traces
    )


# Core API-specific Sentry configuration
def configure_core_sentry(debug: bool = False) -> None:
    """Configure Sentry specifically for Core API component."""
    configure_sentry(
        component="core",
        debug=debug,
        sample_rate=1.0,  # Full sampling for API
        traces_sample_rate=0.1  # Performance monitoring for API
    )
