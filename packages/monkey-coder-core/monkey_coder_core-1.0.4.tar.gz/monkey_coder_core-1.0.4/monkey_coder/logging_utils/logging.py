"""
JSON structured logging configuration for Railway deployment.

This module provides Railway-optimized logging configuration with:
- JSON structured output for better log processing
- Performance tracking for external API calls
- Configurable log levels and filtering
"""

import json
import logging
import os
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

import psutil


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging compatible with Railway.
    
    Converts log records into JSON format with standardized fields
    for better parsing and analysis in Railway's log processing system.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log entry structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add thread and process information
        log_entry["thread"] = record.thread
        log_entry["process"] = record.process
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add Railway-specific fields for better categorization
        log_entry["service"] = "monkey-coder"
        log_entry["environment"] = os.getenv("RAILWAY_ENVIRONMENT", "unknown")
        
        return json.dumps(log_entry, separators=(',', ':'))


class PerformanceLogger:
    """
    Logger for tracking API call performance and system metrics.
    
    Provides decorators and context managers for monitoring
    external API calls and system resource usage.
    """
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_api_call(
        self, 
        func_name: str, 
        duration: float, 
        success: bool, 
        **kwargs
    ) -> None:
        """Log API call performance metrics."""
        extra_fields = {
            "metric_type": "api_call",
            "function": func_name,
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            **kwargs
        }
        
        level = logging.INFO if success else logging.ERROR
        message = f"API call {'completed' if success else 'failed'}: {func_name}"
        
        self.logger.log(level, message, extra={'extra_fields': extra_fields})
    
    def log_system_metrics(self) -> None:
        """Log current system resource usage."""
        try:
            process = psutil.Process()
            
            extra_fields = {
                "metric_type": "system_metrics",
                "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads(),
            }
            
            # Add system-wide metrics if available
            try:
                extra_fields.update({
                    "system_memory_percent": psutil.virtual_memory().percent,
                    "system_cpu_percent": psutil.cpu_percent(),
                    "disk_usage_percent": psutil.disk_usage('/').percent,
                })
            except Exception:
                pass  # Skip system metrics if not available
            
            self.logger.info(
                "System metrics collected", 
                extra={'extra_fields': extra_fields}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")


def monitor_api_calls(logger_name: str = "api_monitor"):
    """
    Decorator for monitoring external API calls.
    
    Args:
        logger_name: Name of the logger to use for API call monitoring
        
    Returns:
        Decorated function with performance monitoring
    """
    performance_logger = PerformanceLogger(logger_name)
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_info = None
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_info = str(e)
                raise
            finally:
                duration = time.time() - start_time
                performance_logger.log_api_call(
                    func_name=func.__name__,
                    duration=duration,
                    success=success,
                    error=error_info,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys())
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_info = None
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_info = str(e)
                raise
            finally:
                duration = time.time() - start_time
                performance_logger.log_api_call(
                    func_name=func.__name__,
                    duration=duration,
                    success=success,
                    error=error_info,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys())
                )
        
        # Return appropriate wrapper based on function type
        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def configure_railway_logging(
    level: str = None, 
    enable_json: bool = None,
    enable_performance: bool = None
) -> None:
    """
    Configure logging for Railway deployment with JSON structured output.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Whether to use JSON formatting (default: True for Railway)
        enable_performance: Whether to enable performance logging (default: True)
    """
    # Get configuration from environment variables
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    json_logs = enable_json if enable_json is not None else os.getenv("JSON_LOGS", "true").lower() == "true"
    perf_logs = enable_performance if enable_performance is not None else os.getenv("PERFORMANCE_LOGS", "true").lower() == "true"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove default handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    
    # Set formatter based on environment
    if json_logs:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    configure_logger_levels()
    
    # Initialize performance logging if enabled
    if perf_logs:
        perf_logger = PerformanceLogger("startup")
        perf_logger.logger.info(
            "Railway logging configuration complete",
            extra={'extra_fields': {
                'log_level': log_level,
                'json_logs': json_logs,
                'performance_logs': perf_logs,
                'environment': os.getenv('RAILWAY_ENVIRONMENT', 'unknown')
            }}
        )


def configure_logger_levels() -> None:
    """Configure specific logger levels to reduce noise."""
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("anthropic").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Keep monkey-coder logs at configured level
    logging.getLogger("monkey_coder").setLevel(logging.INFO)


def get_performance_logger(name: str = "performance") -> PerformanceLogger:
    """Get a performance logger instance."""
    return PerformanceLogger(name)


# Convenience function for application startup
def setup_logging() -> None:
    """Setup logging with Railway-optimized configuration."""
    configure_railway_logging()