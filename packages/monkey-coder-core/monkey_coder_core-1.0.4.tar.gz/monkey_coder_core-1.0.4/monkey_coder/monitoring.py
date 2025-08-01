"""
Monitoring module for metrics collection and billing tracking.

This module provides comprehensive monitoring capabilities for the Monkey Coder Core API,
including execution metrics, usage tracking, billing information, and Prometheus metrics export.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import uuid4

from .models import ExecuteRequest, ExecuteResponse, UsageMetrics

# Initialize logger at module level
logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    # Only log warning after logger is initialized
    logger.warning("Prometheus client not available. Metrics export disabled.")


class MetricsCollector:
    """
    Collects and manages execution metrics for monitoring and analysis.
    Exports metrics to Prometheus when available.
    """

    def __init__(self):
        self.active_executions = {}
        self.completed_executions = []
        
        # Initialize Prometheus metrics if available
        if HAS_PROMETHEUS:
            self.registry = CollectorRegistry()
            
            # Request metrics
            self.http_requests_total = Counter(
                'http_requests_total',
                'Total HTTP requests',
                ['method', 'endpoint', 'status'],
                registry=self.registry
            )
            
            self.http_request_duration_seconds = Histogram(
                'http_request_duration_seconds',
                'HTTP request duration in seconds',
                ['method', 'endpoint'],
                registry=self.registry
            )
            
            # Monkey Coder specific metrics
            self.monkey_coder_requests_total = Counter(
                'monkey_coder_requests_total',
                'Total Monkey Coder API requests',
                ['task_type', 'provider', 'persona'],
                registry=self.registry
            )
            
            self.monkey_coder_tokens_total = Counter(
                'monkey_coder_tokens_total',
                'Total tokens processed',
                ['provider', 'model'],
                registry=self.registry
            )
            
            self.monkey_coder_execution_duration_seconds = Histogram(
                'monkey_coder_execution_duration_seconds',
                'Task execution duration in seconds',
                ['task_type', 'provider'],
                registry=self.registry
            )
            
            self.monkey_coder_active_executions = Gauge(
                'monkey_coder_active_executions',
                'Currently active executions',
                registry=self.registry
            )
            
            self.monkey_coder_errors_total = Counter(
                'monkey_coder_errors_total',
                'Total execution errors',
                ['task_type', 'error_type'],
                registry=self.registry
            )
            
            # Application info
            self.monkey_coder_info = Info(
                'monkey_coder_info',
                'Monkey Coder application information',
                registry=self.registry
            )
            
            self.monkey_coder_info.info({
                'version': '1.0.0',
                'component': 'core'
            })
            
        logger.info("MetricsCollector initialized with Prometheus support: %s", HAS_PROMETHEUS)

    def start_execution(self, request: ExecuteRequest) -> str:
        """
        Start tracking metrics for a new execution.
        
        Args:
            request: The execution request to track
            
        Returns:
            Execution ID for tracking
        """
        execution_id = str(uuid4())
        
        self.active_executions[execution_id] = {
            "request": request,
            "start_time": datetime.utcnow(),
            "task_type": request.task_type,
            "task_id": request.task_id,
        }
        
        # Update Prometheus metrics
        if HAS_PROMETHEUS:
            self.monkey_coder_active_executions.set(len(self.active_executions))
        
        logger.info(f"Started tracking execution: {execution_id}")
        return execution_id

    def complete_execution(self, execution_id: str, response: ExecuteResponse) -> None:
        """
        Complete tracking for an execution.
        
        Args:
            execution_id: The execution ID to complete
            response: The execution response
        """
        if execution_id not in self.active_executions:
            logger.warning(f"Execution {execution_id} not found in active executions")
            return

        execution_data = self.active_executions.pop(execution_id)
        execution_time = (datetime.utcnow() - execution_data["start_time"]).total_seconds()
        
        execution_data.update({
            "end_time": datetime.utcnow(),
            "response": response,
            "status": response.status,
            "execution_time": execution_time,
        })
        
        # Update Prometheus metrics
        if HAS_PROMETHEUS:
            # Request metrics
            self.monkey_coder_requests_total.labels(
                task_type=str(execution_data["task_type"]),
                provider=getattr(response, 'provider', 'unknown'),
                persona=getattr(response, 'persona', 'unknown')
            ).inc()
            
            # Duration metrics
            self.monkey_coder_execution_duration_seconds.labels(
                task_type=str(execution_data["task_type"]),
                provider=getattr(response, 'provider', 'unknown')
            ).observe(execution_time)
            
            # Token metrics
            if hasattr(response, 'usage') and response.usage:
                self.monkey_coder_tokens_total.labels(
                    provider=getattr(response.usage, 'provider', 'unknown'),
                    model=getattr(response.usage, 'model', 'unknown')
                ).inc(getattr(response.usage, 'tokens_used', 0))
            
            # Update active executions gauge
            self.monkey_coder_active_executions.set(len(self.active_executions))
        
        self.completed_executions.append(execution_data)
        logger.info(f"Completed tracking execution: {execution_id}")

    def record_error(self, execution_id: str, error: str) -> None:
        """
        Record an error for an execution.
        
        Args:
            execution_id: The execution ID that errored
            error: Error message
        """
        if execution_id in self.active_executions:
            execution_data = self.active_executions.pop(execution_id)
            execution_time = (datetime.utcnow() - execution_data["start_time"]).total_seconds()
            
            execution_data.update({
                "end_time": datetime.utcnow(),
                "error": error,
                "status": "failed",
                "execution_time": execution_time,
            })
            
            # Update Prometheus metrics
            if HAS_PROMETHEUS:
                # Error metrics
                error_type = "execution_error"
                if "timeout" in error.lower():
                    error_type = "timeout_error"
                elif "authentication" in error.lower():
                    error_type = "auth_error"
                elif "rate limit" in error.lower():
                    error_type = "rate_limit_error"
                
                self.monkey_coder_errors_total.labels(
                    task_type=str(execution_data["task_type"]),
                    error_type=error_type
                ).inc()
                
                # Update active executions gauge
                self.monkey_coder_active_executions.set(len(self.active_executions))
            
            self.completed_executions.append(execution_data)
            logger.info(f"Recorded error for execution: {execution_id}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        total_executions = len(self.completed_executions)
        successful_executions = sum(1 for ex in self.completed_executions if ex.get("status") != "failed")
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": total_executions - successful_executions,
            "active_executions": len(self.active_executions),
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
        }
    
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Record HTTP request metrics for Prometheus."""
        if HAS_PROMETHEUS:
            self.http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=str(status)
            ).inc()
            
            self.http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    def get_prometheus_metrics(self) -> bytes:
        """Get Prometheus metrics in text format."""
        if not HAS_PROMETHEUS:
            return b"# Prometheus client not available\n"
        
        return generate_latest(self.registry)


class BillingTracker:
    """
    Tracks usage and billing information for API usage.
    """

    def __init__(self):
        self.usage_records = []
        logger.info("BillingTracker initialized")

    async def track_usage(self, api_key: str, usage: UsageMetrics) -> None:
        """
        Track usage for billing purposes.
        
        Args:
            api_key: The API key that made the request
            usage: Usage metrics to track
        """
        usage_record = {
            "api_key_hash": self._hash_api_key(api_key),
            "timestamp": datetime.utcnow(),
            "usage": usage,
        }
        
        self.usage_records.append(usage_record)
        logger.info(f"Tracked usage for API key: {usage_record['api_key_hash']}")

    async def get_usage(
        self,
        api_key: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get usage data for an API key.
        
        Args:
            api_key: The API key to get usage for
            start_date: Start date for usage query
            end_date: End date for usage query
            granularity: Granularity of usage data
            
        Returns:
            Usage data dictionary
        """
        api_key_hash = self._hash_api_key(api_key)
        
        # Filter records by API key and date range
        filtered_records = [
            record for record in self.usage_records
            if record["api_key_hash"] == api_key_hash
        ]
        
        if start_date:
            filtered_records = [
                record for record in filtered_records
                if record["timestamp"] >= start_date
            ]
        
        if end_date:
            filtered_records = [
                record for record in filtered_records
                if record["timestamp"] <= end_date
            ]
        
        # Calculate totals
        total_requests = len(filtered_records)
        total_tokens = sum(record["usage"].tokens_used for record in filtered_records)
        total_cost = sum(record["usage"].cost_estimate for record in filtered_records)
        
        return {
            "api_key_hash": api_key_hash,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            },
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "provider_breakdown": [],  # TODO: Implement detailed breakdown
            "execution_stats": {},     # TODO: Implement execution statistics
            "rate_limit_status": [],   # TODO: Implement rate limit tracking
        }

    def _hash_api_key(self, api_key: str) -> str:
        """
        Create a hash of the API key for privacy.
        
        Args:
            api_key: The API key to hash
            
        Returns:
            Hashed API key
        """
        import hashlib
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
