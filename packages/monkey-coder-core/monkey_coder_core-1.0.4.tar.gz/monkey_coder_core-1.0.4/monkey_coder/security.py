"""
Security module for JWT authentication and role-based access control.

This module handles authentication and authorization for the Monkey Coder Core API
following security policies for environment variable usage and MFA support.
"""

import os
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Security configuration from environment variables (as per security policies)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# MFA Configuration
MFA_ENABLED = os.getenv("MFA_ENABLED", "false").lower() == "true"
MFA_ISSUER = os.getenv("MFA_ISSUER", "Monkey Coder")
MFA_SECRET_LENGTH = int(os.getenv("MFA_SECRET_LENGTH", "32"))

# Initialize security components
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if not JWT_SECRET_KEY:
    logger.warning(
        "JWT_SECRET_KEY not set in environment variables. Using temporary key for development."
    )
    JWT_SECRET_KEY = secrets.token_urlsafe(64)


class UserRole(str, Enum):
    """User roles defining access levels and scopes."""

    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    API_USER = "api_user"


class Permission(str, Enum):
    """Granular permissions for different operations."""

    # Core permissions
    CODE_EXECUTE = "code:execute"
    CODE_READ = "code:read"
    CODE_WRITE = "code:write"

    # Sandbox permissions
    SANDBOX_CREATE = "sandbox:create"
    SANDBOX_DELETE = "sandbox:delete"
    SANDBOX_ACCESS = "sandbox:access"

    # Billing permissions
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    BILLING_ADMIN = "billing:admin"

    # Admin permissions
    USER_MANAGE = "user:manage"
    SYSTEM_CONFIG = "system:config"
    METRICS_READ = "metrics:read"


@dataclass
class JWTUser:
    """JWT user claims and metadata."""

    user_id: str
    username: str
    email: str
    roles: List[UserRole]
    permissions: List[Permission]
    mfa_verified: bool = False
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


# Role-based permission mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [
        Permission.CODE_EXECUTE,
        Permission.CODE_READ,
        Permission.CODE_WRITE,
        Permission.SANDBOX_CREATE,
        Permission.SANDBOX_DELETE,
        Permission.SANDBOX_ACCESS,
        Permission.BILLING_READ,
        Permission.BILLING_WRITE,
        Permission.BILLING_ADMIN,
        Permission.USER_MANAGE,
        Permission.SYSTEM_CONFIG,
        Permission.METRICS_READ,
    ],
    UserRole.DEVELOPER: [
        Permission.CODE_EXECUTE,
        Permission.CODE_READ,
        Permission.CODE_WRITE,
        Permission.SANDBOX_CREATE,
        Permission.SANDBOX_ACCESS,
        Permission.BILLING_READ,
        Permission.METRICS_READ,
    ],
    UserRole.VIEWER: [
        Permission.CODE_READ,
        Permission.SANDBOX_ACCESS,
        Permission.BILLING_READ,
    ],
    UserRole.API_USER: [
        Permission.CODE_EXECUTE,
        Permission.CODE_READ,
        Permission.SANDBOX_CREATE,
        Permission.SANDBOX_ACCESS,
    ],
}


def create_access_token(
    user: JWTUser, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for authenticated user.

    Args:
        user: User information and claims
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Build JWT payload with security claims
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "email": user.email,
        "roles": [role.value for role in user.roles],
        "permissions": [perm.value for perm in user.permissions],
        "mfa_verified": user.mfa_verified,
        "session_id": user.session_id or secrets.token_urlsafe(16),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token for token renewal.

    Args:
        user_id: User identifier

    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),  # Unique token ID for revocation
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token or API key.

    Args:
        token: JWT token or API key to verify

    Returns:
        Decoded token payload or API key user payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    # Check if it's an API key
    if token and token.startswith("mk-"):
        if not _validate_api_key(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )

        # Return API key user payload
        return {
            "sub": "api_user",
            "username": "api_user",
            "email": "",
            "roles": ["api_user"],
            "permissions": [
                "code:execute",
                "code:read",
                "billing:read",
                "models:read",
                "providers:read",
                "billing:manage",
                "router:debug",
            ],
            "type": "access",
            "mfa_verified": True,
            "session_id": token[-8:],  # Use last 8 chars as session ID
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": (
                datetime.now(timezone.utc) + timedelta(days=365)
            ).timestamp(),  # API keys don't expire
        }

    # Otherwise, handle as JWT
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Validate token type
        token_type = payload.get("type")
        if token_type not in ["access", "refresh"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except (jwt.InvalidTokenError, jwt.DecodeError, Exception) as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTUser:
    """
    Extract and validate current user from JWT token or API key.

    Args:
        credentials: HTTP authorization credentials containing JWT or API key

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user cannot be authenticated
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
        )

    token = credentials.credentials

    # Handle API keys
    if token and token.startswith("mk-"):
        if not _validate_api_key(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )

        # Return API key user with all necessary permissions
        return JWTUser(
            user_id="api_user",
            username="api_user",
            email="",
            roles=[UserRole.API_USER],
            permissions=[
                Permission.CODE_EXECUTE,
                Permission.CODE_READ,
                Permission.BILLING_READ,
                # Add additional permissions as strings for endpoints that use string permissions
            ],
            mfa_verified=True,
            session_id=token[-8:],  # Use last 8 chars as session ID
        )

    # Handle JWT tokens
    payload = verify_token(token)

    # Extract user information from JWT payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )

    # Build user object from JWT claims
    user = JWTUser(
        user_id=user_id,
        username=payload.get("username", ""),
        email=payload.get("email", ""),
        roles=[UserRole(role) for role in payload.get("roles", [])],
        permissions=[Permission(perm) for perm in payload.get("permissions", [])],
        mfa_verified=payload.get("mfa_verified", False),
        session_id=payload.get("session_id"),
        created_at=datetime.fromtimestamp(payload.get("iat", 0), timezone.utc),
        expires_at=datetime.fromtimestamp(payload.get("exp", 0), timezone.utc),
    )

    # Validate MFA requirement
    if MFA_ENABLED and not user.mfa_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Multi-factor authentication required",
        )

    return user


def require_permission(required_permission: Permission):
    """
    Dependency factory for requiring specific permissions.

    Args:
        required_permission: The permission required to access the endpoint

    Returns:
        FastAPI dependency function
    """

    async def permission_checker(
        current_user: JWTUser = Depends(get_current_user),
    ) -> JWTUser:
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {required_permission.value} required",
            )
        return current_user

    return permission_checker


def require_role(required_role: UserRole):
    """
    Dependency factory for requiring specific roles.

    Args:
        required_role: The role required to access the endpoint

    Returns:
        FastAPI dependency function
    """

    async def role_checker(
        current_user: JWTUser = Depends(get_current_user),
    ) -> JWTUser:
        if required_role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role: {required_role.value} required",
            )
        return current_user

    return role_checker


def get_user_permissions(roles: List[UserRole]) -> List[Permission]:
    """
    Get all permissions for a list of user roles.

    Args:
        roles: List of user roles

    Returns:
        Combined list of unique permissions
    """
    permissions = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, []))
    return list(permissions)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_mfa_secret() -> str:
    """
    Generate a new MFA secret key.

    Returns:
        Base32-encoded secret key
    """
    import base64

    secret_bytes = secrets.token_bytes(MFA_SECRET_LENGTH)
    return base64.b32encode(secret_bytes).decode("utf-8")


def generate_mfa_qr_uri(user_email: str, secret: str) -> str:
    """
    Generate MFA QR code URI for authenticator apps.

    Args:
        user_email: User's email address
        secret: MFA secret key

    Returns:
        QR code URI string
    """
    from urllib.parse import quote

    return f"otpauth://totp/{quote(MFA_ISSUER)}:{quote(user_email)}?secret={secret}&issuer={quote(MFA_ISSUER)}"


def verify_mfa_token(secret: str, token: str, window: int = 1) -> bool:
    """
    Verify MFA TOTP token.

    Args:
        secret: MFA secret key
        token: TOTP token to verify
        window: Time window for token validation (default: 1)

    Returns:
        True if token is valid, False otherwise
    """
    try:
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)
    except ImportError:
        logger.warning("pyotp not installed, MFA verification disabled")
        return True  # Allow access if MFA library not available
    except Exception as e:
        logger.error(f"MFA verification failed: {e}")
        return False


# Legacy API key support for backward compatibility
async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Enhanced API key validation with proper key management.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Valid API key string

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required"
        )

    api_key = credentials.credentials

    # Try JWT token first, fall back to API key validation
    try:
        verify_token(api_key)
        return api_key
    except HTTPException:
        # Import here to avoid circular dependency
        from .auth import get_api_key_manager

        # Use API key manager for validation
        api_key_manager = get_api_key_manager()
        key_info = api_key_manager.validate_api_key(api_key)

        if not key_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key or token",
            )

        return api_key


def _validate_api_key(api_key: str) -> bool:
    """
    Legacy API key format validation (deprecated - use APIKeyManager).

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    return api_key and api_key.startswith("mk-") and len(api_key) > 10


async def verify_permissions(api_key: str, permission: str = None) -> bool:
    """
    Verify permissions for API key using the API key manager.

    Args:
        api_key: The API key to verify permissions for
        permission: The specific permission to check (optional)

    Returns:
        True if permissions are valid
    """
    # Import here to avoid circular dependency
    from .auth import get_api_key_manager

    # Use API key manager for validation and permission checking
    api_key_manager = get_api_key_manager()
    key_info = api_key_manager.validate_api_key(api_key)

    if not key_info:
        return False

    # If no specific permission requested, just validate the key
    if not permission:
        return True

    # Check specific permission
    return api_key_manager.check_permission(key_info, permission)


# Legacy User Store has been replaced with database-backed implementation
# See monkey_coder.database.user_store and monkey_coder.database.models for current implementation
