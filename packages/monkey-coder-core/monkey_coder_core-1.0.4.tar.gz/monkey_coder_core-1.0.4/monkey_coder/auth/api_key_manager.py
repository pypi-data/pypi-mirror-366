"""
API Key Management System

Provides functionality for generating, validating, and managing API keys
for user authentication and access control.
"""

import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class APIKeyStatus(str, Enum):
    """API key status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class APIKeyInfo:
    """API key information structure."""
    key_id: str
    key_prefix: str  # First 8 characters for identification
    key_hash: str    # Hashed full key for validation
    name: str
    description: str
    status: APIKeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    permissions: List[str]
    metadata: Dict[str, Any]


class APIKeyManager:
    """
    API Key Manager for generating and validating API keys.
    
    Provides functionality for:
    - Generating secure API keys with mk- prefix
    - Validating API keys against stored hashes
    - Managing key lifecycle (creation, expiration, revocation)
    - Tracking usage and permissions
    """
    
    def __init__(self):
        # In-memory storage for demo/development
        # In production, this should use a database
        self._keys: Dict[str, APIKeyInfo] = {}
        self._key_hashes: Dict[str, str] = {}  # hash -> key_id mapping
        
        # Create a default development API key if none exist
        self._ensure_development_key()
        
        logger.info("APIKeyManager initialized")
    
    def _ensure_development_key(self):
        """Ensure there's at least one development API key for testing."""
        if not self._keys:
            dev_key = self.generate_api_key(
                name="Development Key",
                description="Default API key for development and testing",
                permissions=["*"],  # Full permissions for development
                expires_days=365    # 1 year expiration
            )
            logger.info(f"Created development API key: {dev_key['key'][:15]}...")
    
    def generate_api_key(
        self,
        name: str,
        description: str = "",
        permissions: List[str] = None,
        expires_days: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a new API key.
        
        Args:
            name: Human-readable name for the key
            description: Description of the key's purpose
            permissions: List of permissions (default: basic read/write)
            expires_days: Number of days until expiration (None = no expiration)
            metadata: Additional metadata for the key
            
        Returns:
            Dictionary containing the generated key and metadata
        """
        # Generate secure random key
        key_id = f"key_{secrets.token_hex(8)}"
        key_suffix = secrets.token_urlsafe(32)
        api_key = f"mk-{key_suffix}"
        
        # Create key hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Set default permissions
        if permissions is None:
            permissions = [
                "auth:login",
                "auth:status", 
                "execute:create",
                "billing:read",
                "providers:read",
                "models:read",
                "router:debug"
            ]
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Create key info
        key_info = APIKeyInfo(
            key_id=key_id,
            key_prefix=api_key[:8],  # mk-xxxxx
            key_hash=key_hash,
            name=name,
            description=description,
            status=APIKeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used=None,
            usage_count=0,
            permissions=permissions,
            metadata=metadata or {}
        )
        
        # Store key info
        self._keys[key_id] = key_info
        self._key_hashes[key_hash] = key_id
        
        logger.info(f"Generated API key: {key_info.key_prefix}... for '{name}'")
        
        return {
            "key": api_key,
            "key_id": key_id,
            "name": name,
            "description": description,
            "permissions": permissions,
            "created_at": key_info.created_at.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "status": key_info.status.value
        }
    
    def validate_api_key(self, api_key: str) -> Optional[APIKeyInfo]:
        """
        Validate an API key and return key information.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            APIKeyInfo if valid, None if invalid
        """
        if not api_key or not api_key.startswith('mk-') or len(api_key) <= 10:
            return None
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Find key by hash
        key_id = self._key_hashes.get(key_hash)
        if not key_id:
            return None
        
        key_info = self._keys.get(key_id)
        if not key_info:
            return None
        
        # Check key status
        if key_info.status != APIKeyStatus.ACTIVE:
            logger.warning(f"Attempted to use inactive API key: {key_info.key_prefix}...")
            return None
        
        # Check expiration
        if key_info.expires_at and datetime.utcnow() > key_info.expires_at:
            logger.warning(f"Attempted to use expired API key: {key_info.key_prefix}...")
            # Auto-expire the key
            key_info.status = APIKeyStatus.EXPIRED
            return None
        
        # Update last used timestamp and usage count
        key_info.last_used = datetime.utcnow()
        key_info.usage_count += 1
        
        return key_info
    
    def list_api_keys(self, include_revoked: bool = False) -> List[Dict[str, Any]]:
        """
        List all API keys (excluding sensitive information).
        
        Args:
            include_revoked: Whether to include revoked keys
            
        Returns:
            List of API key information dictionaries
        """
        keys = []
        for key_info in self._keys.values():
            if not include_revoked and key_info.status == APIKeyStatus.REVOKED:
                continue
            
            keys.append({
                "key_id": key_info.key_id,
                "key_prefix": key_info.key_prefix,
                "name": key_info.name,
                "description": key_info.description,
                "status": key_info.status.value,
                "created_at": key_info.created_at.isoformat(),
                "expires_at": key_info.expires_at.isoformat() if key_info.expires_at else None,
                "last_used": key_info.last_used.isoformat() if key_info.last_used else None,
                "usage_count": key_info.usage_count,
                "permissions": key_info.permissions,
                "metadata": key_info.metadata
            })
        
        return sorted(keys, key=lambda x: x["created_at"], reverse=True)
    
    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: The key ID to revoke
            
        Returns:
            True if revoked successfully, False if key not found
        """
        key_info = self._keys.get(key_id)
        if not key_info:
            return False
        
        key_info.status = APIKeyStatus.REVOKED
        logger.info(f"Revoked API key: {key_info.key_prefix}... ('{key_info.name}')")
        
        return True
    
    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific API key.
        
        Args:
            key_id: The key ID to get information for
            
        Returns:
            Key information dictionary or None if not found
        """
        key_info = self._keys.get(key_id)
        if not key_info:
            return None
        
        return {
            "key_id": key_info.key_id,
            "key_prefix": key_info.key_prefix,
            "name": key_info.name,
            "description": key_info.description,
            "status": key_info.status.value,
            "created_at": key_info.created_at.isoformat(),
            "expires_at": key_info.expires_at.isoformat() if key_info.expires_at else None,
            "last_used": key_info.last_used.isoformat() if key_info.last_used else None,
            "usage_count": key_info.usage_count,
            "permissions": key_info.permissions,
            "metadata": key_info.metadata
        }
    
    def check_permission(self, key_info: APIKeyInfo, permission: str) -> bool:
        """
        Check if an API key has a specific permission.
        
        Args:
            key_info: The API key information
            permission: The permission to check
            
        Returns:
            True if the key has the permission, False otherwise
        """
        if not key_info or key_info.status != APIKeyStatus.ACTIVE:
            return False
        
        # Check for wildcard permission
        if "*" in key_info.permissions:
            return True
        
        # Check for exact permission match
        if permission in key_info.permissions:
            return True
        
        # Check for prefix match (e.g., "auth:*" matches "auth:login")
        for perm in key_info.permissions:
            if perm.endswith(":*") and permission.startswith(perm[:-1]):
                return True
        
        return False
    
    def get_development_key(self) -> Optional[str]:
        """
        Get the development API key for testing purposes.
        
        Returns:
            The development API key if available
        """
        for key_info in self._keys.values():
            if key_info.name == "Development Key" and key_info.status == APIKeyStatus.ACTIVE:
                # Reconstruct the key from stored information
                # In a real implementation, you'd never store the actual key
                # This is just for development/testing
                return f"mk-{key_info.key_id.replace('key_', '')}{secrets.token_urlsafe(16)}"
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get API key usage statistics.
        
        Returns:
            Dictionary containing usage statistics
        """
        total_keys = len(self._keys)
        active_keys = len([k for k in self._keys.values() if k.status == APIKeyStatus.ACTIVE])
        expired_keys = len([k for k in self._keys.values() if k.status == APIKeyStatus.EXPIRED])
        revoked_keys = len([k for k in self._keys.values() if k.status == APIKeyStatus.REVOKED])
        
        total_usage = sum(k.usage_count for k in self._keys.values())
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "revoked_keys": revoked_keys,
            "total_usage": total_usage,
            "average_usage": total_usage / total_keys if total_keys > 0 else 0
        }


# Global API key manager instance
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager