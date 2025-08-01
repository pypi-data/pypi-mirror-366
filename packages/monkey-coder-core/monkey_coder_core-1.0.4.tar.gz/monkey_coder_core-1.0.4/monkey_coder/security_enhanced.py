"""
Enhanced security module with httpOnly cookie support and secure token management.

This module provides enhanced security features including:
- httpOnly cookie-based authentication
- CSRF protection
- Secure token storage and validation
- Session management with Redis
- Advanced security headers
"""

import os
import logging
import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any, Union, cast
from enum import Enum
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

import jwt
from fastapi import HTTPException, Depends, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from cryptography.fernet import Fernet
import redis.asyncio as redis

from .security import (
    JWTUser,
    UserRole,
    Permission,
    ROLE_PERMISSIONS,
    get_user_permissions,
    hash_password,
    verify_password,
    create_access_token as create_jwt_token,
    create_refresh_token as create_jwt_refresh_token,
    verify_token as verify_jwt_token,
)

logger = logging.getLogger(__name__)

# Enhanced security configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", secrets.token_urlsafe(32))
COOKIE_SECRET_KEY = os.getenv("COOKIE_SECRET_KEY", secrets.token_urlsafe(32))
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))

# Cookie configuration
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")  # lax, strict, or none
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
CSRF_TOKEN_COOKIE_NAME = "csrf_token"
SESSION_COOKIE_NAME = "session_id"

# Session configuration
SESSION_EXPIRE_MINUTES = int(os.getenv("SESSION_EXPIRE_MINUTES", "1440"))  # 24 hours
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Security headers configuration
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# Initialize security components
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
csrf_serializer = URLSafeTimedSerializer(CSRF_SECRET_KEY, salt="csrf-protection")
cookie_serializer = URLSafeTimedSerializer(COOKIE_SECRET_KEY, salt="cookie-auth")
session_serializer = URLSafeTimedSerializer(SESSION_SECRET_KEY, salt="session-mgmt")

# Initialize Redis client for session storage
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Initialize Fernet for sensitive data encryption
fernet_key = os.getenv("FERNET_KEY") or Fernet.generate_key()
fernet = Fernet(fernet_key)


class SessionType(str, Enum):
    """Session types for different authentication flows."""

    WEB = "web"
    API = "api"
    CLI = "cli"
    MOBILE = "mobile"


@dataclass
class SessionData:
    """Session data structure for Redis storage."""

    session_id: str
    user_id: str
    session_type: SessionType
    user_agent: str
    ip_address: str
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    is_active: bool
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert session data to dictionary for Redis storage."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        data["last_accessed"] = self.last_accessed.isoformat()
        data["session_type"] = self.session_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create session data from dictionary."""
        # Convert ISO strings back to datetime objects
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        data["session_type"] = SessionType(data["session_type"])
        return cls(**data)


class CookieAuthManager:
    """Manager for cookie-based authentication with httpOnly support."""

    def __init__(self):
        self.redis_client = redis_client

    async def create_session(
        self,
        user: JWTUser,
        request: Request,
        session_type: SessionType = SessionType.WEB,
        remember_me: bool = False
    ) -> SessionData:
        """Create a new session for the user."""
        session_id = secrets.token_urlsafe(32)

        # Calculate expiration time
        if remember_me:
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=SESSION_EXPIRE_MINUTES)

        # Create session data
        session_data = SessionData(
            session_id=session_id,
            user_id=user.user_id,
            session_type=session_type,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host if request.client else "",
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            last_accessed=datetime.now(timezone.utc),
            is_active=True,
            metadata={
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions],
                "mfa_verified": user.mfa_verified,
            }
        )

        # Store session in Redis
        await self.redis_client.setex(
            f"session:{session_id}",
            int((expires_at - datetime.now(timezone.utc)).total_seconds()),
            json.dumps(session_data.to_dict())
        )

        # Store user session mapping
        await self.redis_client.sadd(f"user_sessions:{user.user_id}", session_id)

        return session_data

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data from Redis."""
        session_json = await self.redis_client.get(f"session:{session_id}")
        if not session_json:
            return None

        try:
            session_data = SessionData.from_dict(json.loads(session_json))

            # Check if session is expired
            if session_data.expires_at < datetime.now(timezone.utc):
                await self.delete_session(session_id)
                return None

            # Update last accessed time
            session_data.last_accessed = datetime.now(timezone.utc)
            await self.redis_client.setex(
                f"session:{session_id}",
                int((session_data.expires_at - datetime.now(timezone.utc)).total_seconds()),
                json.dumps(session_data.to_dict())
            )

            return session_data
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis."""
        try:
            # Get session data to remove user session mapping
            session_json = await self.redis_client.get(f"session:{session_id}")
            if session_json:
                session_data = SessionData.from_dict(json.loads(session_json))
                await self.redis_client.srem(f"user_sessions:{session_data.user_id}", session_id)

            # Delete session
            await self.redis_client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

    async def delete_user_sessions(self, user_id: str, exclude_session_id: Optional[str] = None) -> int:
        """Delete all sessions for a user except the specified one."""
        try:
            session_ids = await self.redis_client.smembers(f"user_sessions:{user_id}")
            deleted_count = 0

            for session_id in session_ids:
                if session_id != exclude_session_id:
                    if await self.delete_session(session_id):
                        deleted_count += 1

            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting user sessions for {user_id}: {e}")
            return 0

    def create_access_token_cookie(self, token: str, expires_delta: timedelta) -> Dict[str, Any]:
        """Create access token cookie settings."""
        return {
            "key": ACCESS_TOKEN_COOKIE_NAME,
            "value": token,
            "max_age": int(expires_delta.total_seconds()),
            "expires": expires_delta,
            "httponly": True,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
        }

    def create_refresh_token_cookie(self, token: str, expires_delta: timedelta) -> Dict[str, Any]:
        """Create refresh token cookie settings."""
        return {
            "key": REFRESH_TOKEN_COOKIE_NAME,
            "value": token,
            "max_age": int(expires_delta.total_seconds()),
            "expires": expires_delta,
            "httponly": True,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
        }

    def create_csrf_token_cookie(self, token: str, expires_delta: timedelta) -> Dict[str, Any]:
        """Create CSRF token cookie settings."""
        return {
            "key": CSRF_TOKEN_COOKIE_NAME,
            "value": token,
            "max_age": int(expires_delta.total_seconds()),
            "expires": expires_delta,
            "httponly": False,  # JavaScript needs access to CSRF token
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
        }

    def create_session_cookie(self, session_id: str, expires_delta: timedelta) -> Dict[str, Any]:
        """Create session ID cookie settings."""
        return {
            "key": SESSION_COOKIE_NAME,
            "value": session_id,
            "max_age": int(expires_delta.total_seconds()),
            "expires": expires_delta,
            "httponly": True,
            "secure": COOKIE_SECURE,
            "samesite": COOKIE_SAMESITE,
            "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
        }

    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        return csrf_serializer.dumps(session_id)

    def verify_csrf_token(self, token: str, session_id: str) -> bool:
        """Verify CSRF token for session."""
        try:
            decoded_session_id = csrf_serializer.loads(
                token,
                max_age=3600  # 1 hour
            )
            return decoded_session_id == session_id
        except Exception:
            return False

    def clear_auth_cookies(self) -> List[Dict[str, Any]]:
        """Clear all authentication cookies."""
        return [
            {
                "key": ACCESS_TOKEN_COOKIE_NAME,
                "value": "",
                "max_age": 0,
                "expires": timedelta(seconds=0),
                "httponly": True,
                "secure": COOKIE_SECURE,
                "samesite": COOKIE_SAMESITE,
                "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
            },
            {
                "key": REFRESH_TOKEN_COOKIE_NAME,
                "value": "",
                "max_age": 0,
                "expires": timedelta(seconds=0),
                "httponly": True,
                "secure": COOKIE_SECURE,
                "samesite": COOKIE_SAMESITE,
                "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
            },
            {
                "key": CSRF_TOKEN_COOKIE_NAME,
                "value": "",
                "max_age": 0,
                "expires": timedelta(seconds=0),
                "httponly": False,
                "secure": COOKIE_SECURE,
                "samesite": COOKIE_SAMESITE,
                "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
            },
            {
                "key": SESSION_COOKIE_NAME,
                "value": "",
                "max_age": 0,
                "expires": timedelta(seconds=0),
                "httponly": True,
                "secure": COOKIE_SECURE,
                "samesite": COOKIE_SAMESITE,
                "domain": COOKIE_DOMAIN if COOKIE_DOMAIN else None,
            },
        ]


# Global cookie auth manager instance
cookie_auth_manager = CookieAuthManager()


async def get_current_user_enhanced(
    request: Request,
    csrf_token: Optional[str] = None
) -> JWTUser:
    """
    Enhanced current user extraction supporting both JWT tokens and httpOnly cookies.

    Args:
        request: FastAPI request object
        csrf_token: Optional CSRF token for cookie-based authentication

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    # First, try Bearer token authentication (for API/CLI usage)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix

        # Handle API keys
        if token.startswith("mk-"):
            from .auth import get_api_key_manager
            api_key_manager = get_api_key_manager()
            key_info = api_key_manager.validate_api_key(token)

            if not key_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )

            return JWTUser(
                user_id="api_user",
                username="api_user",
                email="",
                roles=[UserRole.API_USER],
                permissions=[
                    Permission.CODE_EXECUTE,
                    Permission.CODE_READ,
                    Permission.BILLING_READ,
                ],
                mfa_verified=True,
                session_id=token[-8:],
            )

        # Handle JWT tokens
        try:
            payload = verify_jwt_token(token)

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )

            return JWTUser(
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
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    # Fall back to cookie-based authentication (for web usage)
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Get session data
    session_data = await cookie_auth_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    # Verify CSRF token for state-changing requests
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token required"
            )

        stored_csrf_token = request.cookies.get(CSRF_TOKEN_COOKIE_NAME)
        if not stored_csrf_token or not cookie_auth_manager.verify_csrf_token(csrf_token, session_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )

    # Create JWT user from session data
    return JWTUser(
        user_id=session_data.user_id,
        username="",  # Will be populated from database if needed
        email="",
        roles=[UserRole(role) for role in session_data.metadata.get("roles", [])],
        permissions=[Permission(perm) for perm in session_data.metadata.get("permissions", [])],
        mfa_verified=session_data.metadata.get("mfa_verified", False),
        session_id=session_id,
    )


def add_security_headers(response: Union[Response, JSONResponse]) -> Union[Response, JSONResponse]:
    """Add security headers to response."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


def create_auth_response(
    user: JWTUser,
    session_data: SessionData,
    access_token: str,
    refresh_token: str,
    response_data: Dict[str, Any]
) -> JSONResponse:
    """
    Create authentication response with httpOnly cookies and security headers.

    Args:
        user: Authenticated user
        session_data: Session data
        access_token: JWT access token
        refresh_token: JWT refresh token
        response_data: Response data payload

    Returns:
        JSONResponse with cookies and security headers
    """
    # Calculate expiration times
    access_expires = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    refresh_expires = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")))
    session_expires = session_data.expires_at - datetime.now(timezone.utc)

    # Generate CSRF token
    csrf_token = cookie_auth_manager.generate_csrf_token(session_data.session_id)

    # Create response
    response = JSONResponse(content=response_data)

    # Add security headers
    response = cast(JSONResponse, add_security_headers(response))

    # Set cookies
    response.set_cookie(**cookie_auth_manager.create_access_token_cookie(access_token, access_expires))
    response.set_cookie(**cookie_auth_manager.create_refresh_token_cookie(refresh_token, refresh_expires))
    response.set_cookie(**cookie_auth_manager.create_csrf_token_cookie(csrf_token, access_expires))
    response.set_cookie(**cookie_auth_manager.create_session_cookie(session_data.session_id, session_expires))

    return response


def create_logout_response() -> JSONResponse:
    """Create logout response that clears all authentication cookies."""
    response = JSONResponse(content={"message": "Successfully logged out"})
    response = cast(JSONResponse, add_security_headers(response))

    # Clear all auth cookies
    for cookie_settings in cookie_auth_manager.clear_auth_cookies():
        response.set_cookie(**cookie_settings)

    return response


async def require_permission_enhanced(
    required_permission: Permission,
    request: Request,
    csrf_token: Optional[str] = None
) -> JWTUser:
    """
    Enhanced permission checker supporting both token and cookie authentication.

    Args:
        required_permission: The permission required to access the endpoint
        request: FastAPI request object
        csrf_token: Optional CSRF token for cookie-based authentication

    Returns:
        Current authenticated user with verified permissions

    Raises:
        HTTPException: If permissions are insufficient
    """
    current_user = await get_current_user_enhanced(request, csrf_token)

    if required_permission not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: {required_permission.value} required"
        )

    return current_user


async def require_role_enhanced(
    required_role: UserRole,
    request: Request,
    csrf_token: Optional[str] = None
) -> JWTUser:
    """
    Enhanced role checker supporting both token and cookie authentication.

    Args:
        required_role: The role required to access the endpoint
        request: FastAPI request object
        csrf_token: Optional CSRF token for cookie-based authentication

    Returns:
        Current authenticated user with verified role

    Raises:
        HTTPException: If role is insufficient
    """
    current_user = await get_current_user_enhanced(request, csrf_token)

    if required_role not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient role: {required_role.value} required"
        )

    return current_user
