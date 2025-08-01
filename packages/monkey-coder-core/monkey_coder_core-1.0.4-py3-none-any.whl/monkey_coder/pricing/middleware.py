"""
Pricing middleware for automatic usage tracking.

This middleware automatically records usage events to the database
with pricing information for billing purposes.
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..database.models import UsageEvent
from ..models import UsageMetrics
from .models import get_model_pricing

logger = logging.getLogger(__name__)


class PricingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically track usage and pricing for API requests.
    
    This middleware intercepts API requests and responses to extract
    usage information and record it for billing purposes.
    """
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and track usage.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint to call
            
        Returns:
            Response: HTTP response
        """
        if not self.enabled:
            return await call_next(request)
        
        # Only track usage for execute endpoints
        if not request.url.path.startswith("/v1/execute"):
            return await call_next(request)
        
        # Get API key for tracking
        api_key = self._extract_api_key(request)
        if not api_key:
            # No API key found, skip tracking
            return await call_next(request)
        
        # Hash API key for privacy
        api_key_hash = self._hash_api_key(api_key)
        
        # Record start time
        start_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        # Record end time
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        # Extract usage information from response
        try:
            await self._record_usage_event(
                request=request,
                response=response,
                api_key_hash=api_key_hash,
                execution_time=execution_time,
                start_time=start_time
            )
        except Exception as e:
            logger.error(f"Failed to record usage event: {e}")
            # Don't fail the request if usage tracking fails
        
        return response
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """
        Extract API key from request.
        
        Args:
            request: FastAPI request
            
        Returns:
            Optional[str]: API key if found
        """
        # Check Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")
        
        # Check X-API-Key header
        api_key = request.headers.get("x-api-key")
        if api_key:
            return api_key
        
        # Check query parameter
        api_key = request.query_params.get("api_key")
        if api_key:
            return api_key
        
        return None
    
    def _hash_api_key(self, api_key: str) -> str:
        """
        Create a hash of the API key for privacy.
        
        Args:
            api_key: The API key to hash
            
        Returns:
            str: Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    async def _record_usage_event(
        self,
        request: Request,
        response: Response,
        api_key_hash: str,
        execution_time: float,
        start_time: datetime
    ) -> None:
        """
        Record usage event to database.
        
        Args:
            request: FastAPI request
            response: FastAPI response
            api_key_hash: Hashed API key
            execution_time: Execution time in seconds
            start_time: Request start time
        """
        try:
            # Extract usage information from response
            usage_info = await self._extract_usage_from_response(response)
            if not usage_info:
                logger.debug("No usage information found in response")
                return
            
            # Get pricing information
            model_pricing = get_model_pricing(usage_info["model"])
            if not model_pricing:
                logger.warning(f"No pricing information found for model: {usage_info['model']}")
                # Use default pricing to avoid losing usage data
                input_cost_per_token = 0.000001  # $1 per 1M tokens default
                output_cost_per_token = 0.000003  # $3 per 1M tokens default
            else:
                input_cost_per_token = model_pricing.input_cost_per_token
                output_cost_per_token = model_pricing.output_cost_per_token
            
            # Calculate costs
            input_cost = usage_info["tokens_input"] * input_cost_per_token
            output_cost = usage_info["tokens_output"] * output_cost_per_token
            total_cost = input_cost + output_cost
            
            # Extract additional metadata
            metadata = {
                "user_agent": request.headers.get("user-agent", ""),
                "request_id": response.headers.get("x-request-id", ""),
                "response_status": response.status_code,
            }
            
            # Create usage event
            await UsageEvent.create(
                api_key_hash=api_key_hash,
                execution_id=usage_info["execution_id"],
                task_type=usage_info["task_type"],
                
                # Token usage
                tokens_input=usage_info["tokens_input"],
                tokens_output=usage_info["tokens_output"],
                tokens_total=usage_info["tokens_input"] + usage_info["tokens_output"],
                
                # Provider and model info
                provider=usage_info["provider"],
                model=usage_info["model"],
                model_cost_input=input_cost_per_token,
                model_cost_output=output_cost_per_token,
                
                # Calculated costs
                cost_input=input_cost,
                cost_output=output_cost,
                cost_total=total_cost,
                
                # Execution metadata
                execution_time=execution_time,
                status=usage_info.get("status", "completed"),
                error_message=usage_info.get("error_message"),
                
                # Timestamps
                created_at=start_time,
                
                # Additional metadata
                metadata=metadata
            )
            
            logger.info(f"Recorded usage event: {usage_info['execution_id']} - ${total_cost:.6f}")
            
        except Exception as e:
            logger.error(f"Failed to record usage event: {e}")
            raise
    
    async def _extract_usage_from_response(self, response: Response) -> Optional[Dict[str, Any]]:
        """
        Extract usage information from API response.
        
        Args:
            response: FastAPI response
            
        Returns:
            Optional[Dict]: Usage information if available
        """
        try:
            # For successful responses, usage info should be in the response body
            if response.status_code == 200:
                # In a real implementation, you'd parse the response body
                # For now, we'll use response headers or state if available
                
                # Check if usage info is stored in response state
                if hasattr(response, "usage_info"):
                    return response.usage_info
                
                # Check response headers for usage info
                execution_id = response.headers.get("x-execution-id")
                if execution_id:
                    # Try to extract from headers (fallback method)
                    return {
                        "execution_id": execution_id,
                        "task_type": response.headers.get("x-task-type", "unknown"),
                        "provider": response.headers.get("x-provider", "unknown"),
                        "model": response.headers.get("x-model", "unknown"),
                        "tokens_input": int(response.headers.get("x-tokens-input", "0")),
                        "tokens_output": int(response.headers.get("x-tokens-output", "0")),
                        "status": "completed" if response.status_code == 200 else "failed"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract usage from response: {e}")
            return None


def attach_usage_info_to_response(
    response: Response,
    execution_id: str,
    task_type: str,
    provider: str,
    model: str,
    tokens_input: int,
    tokens_output: int,
    status: str = "completed",
    error_message: Optional[str] = None
) -> None:
    """
    Attach usage information to response for middleware tracking.
    
    This helper function should be called from API endpoints to attach
    usage information to the response so the middleware can track it.
    
    Args:
        response: FastAPI response object
        execution_id: Unique execution identifier
        task_type: Type of task executed
        provider: AI provider used
        model: Model used
        tokens_input: Input tokens consumed
        tokens_output: Output tokens generated
        status: Execution status
        error_message: Error message if failed
    """
    response.usage_info = {
        "execution_id": execution_id,
        "task_type": task_type,
        "provider": provider,
        "model": model,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "status": status,
        "error_message": error_message,
    }
    
    # Also set headers for fallback extraction
    response.headers["x-execution-id"] = execution_id
    response.headers["x-task-type"] = task_type
    response.headers["x-provider"] = provider
    response.headers["x-model"] = model
    response.headers["x-tokens-input"] = str(tokens_input)
    response.headers["x-tokens-output"] = str(tokens_output)
