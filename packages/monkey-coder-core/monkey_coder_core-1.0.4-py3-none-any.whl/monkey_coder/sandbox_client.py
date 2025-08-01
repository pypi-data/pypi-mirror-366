"""
Sandbox Client Integration

Provides interface for core application to communicate with sandbox service.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from .security import generate_sandbox_token

logger = logging.getLogger(__name__)


class SandboxRequest(BaseModel):
    """Request model for sandbox operations."""
    sandbox_type: str
    action: str
    code: Optional[str] = None
    url: Optional[str] = None
    timeout: int = 30
    metadata: Dict[str, Any] = {}


class SandboxResponse(BaseModel):
    """Response model from sandbox service."""
    execution_id: str
    status: str
    result: Any = None
    logs: list = []
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = {}


class SandboxClient:
    """Client for communicating with the sandbox service."""
    
    def __init__(self):
        self.sandbox_url = os.getenv("SANDBOX_SERVICE_URL", "http://localhost:8001")
        self.token_secret = os.getenv("SANDBOX_TOKEN_SECRET", "default-secret")
        self.timeout = 60  # Default timeout for HTTP requests
        
    async def execute_code(
        self,
        code: str,
        execution_id: str,
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code in E2B sandbox.
        
        Args:
            code: Python code to execute
            execution_id: Unique execution identifier
            timeout: Execution timeout in seconds
            metadata: Additional execution metadata
            
        Returns:
            Dictionary containing execution results
        """
        request = SandboxRequest(
            sandbox_type="code",
            action="execute",
            code=code,
            timeout=timeout,
            metadata=metadata or {}
        )
        
        return await self._make_sandbox_request(request, execution_id)
    
    async def execute_browser_action(
        self,
        url: str,
        action: str,
        execution_id: str,
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute browser automation action using BrowserBase.
        
        Args:
            url: Target URL
            action: Browser action to perform
            execution_id: Unique execution identifier
            timeout: Execution timeout in seconds
            metadata: Additional execution metadata
            
        Returns:
            Dictionary containing action results
        """
        request = SandboxRequest(
            sandbox_type="browser",
            action=action,
            url=url,
            timeout=timeout,
            metadata=metadata or {}
        )
        
        return await self._make_sandbox_request(request, execution_id)
    
    async def _make_sandbox_request(
        self,
        request: SandboxRequest,
        execution_id: str
    ) -> Dict[str, Any]:
        """Make authenticated request to sandbox service."""
        try:
            # Generate sandbox token
            token = self._generate_token(execution_id)
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Make request to sandbox service
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.sandbox_url}/sandbox/execute",
                    json=request.dict(),
                    headers=headers
                )
                response.raise_for_status()
                
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Sandbox request timeout for {execution_id}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "result": None,
                "logs": ["Sandbox request timed out"],
                "error": "TIMEOUT"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Sandbox HTTP error for {execution_id}: {e.response.status_code}")
            return {
                "execution_id": execution_id,
                "status": "error", 
                "result": None,
                "logs": [f"HTTP {e.response.status_code}: {e.response.text}"],
                "error": f"HTTP_{e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"Sandbox request failed for {execution_id}: {str(e)}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "result": None,
                "logs": [f"Request failed: {str(e)}"],
                "error": str(e)
            }
    
    def _generate_token(self, execution_id: str) -> str:
        """Generate authentication token for sandbox request."""
        # For now, use a simple implementation
        # In production, this should use proper JWT with the sandbox service
        return generate_sandbox_token(execution_id, expires_in=3600)
    
    async def get_sandbox_metrics(self) -> Dict[str, Any]:
        """Get sandbox service metrics."""
        try:
            token = self._generate_token("metrics")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.sandbox_url}/sandbox/metrics",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get sandbox metrics: {str(e)}")
            return {}
    
    async def cleanup_sandbox_resources(self) -> Dict[str, Any]:
        """Trigger cleanup of idle sandbox resources."""
        try:
            token = self._generate_token("cleanup")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.sandbox_url}/sandbox/cleanup",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to cleanup sandbox resources: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def health_check(self) -> bool:
        """Check if sandbox service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.sandbox_url}/sandbox/health")
                return response.status_code == 200
        except Exception:
            return False


def generate_sandbox_token(execution_id: str, expires_in: int = 3600) -> str:
    """
    Generate a secure token for sandbox operations.
    
    This is a simplified implementation. In production, use proper JWT.
    """
    import base64
    import hashlib
    import hmac
    import json
    
    secret = os.getenv("SANDBOX_TOKEN_SECRET", "default-secret")
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    payload = {
        "execution_id": execution_id,
        "expires_at": expires_at.isoformat(),
    }
    
    payload_json = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    token_data = {
        "payload": payload,
        "signature": signature
    }
    
    token_json = json.dumps(token_data)
    return base64.b64encode(token_json.encode()).decode()
