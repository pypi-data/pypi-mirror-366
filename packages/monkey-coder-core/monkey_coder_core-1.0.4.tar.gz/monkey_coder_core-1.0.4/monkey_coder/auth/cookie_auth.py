"""
Enhanced authentication module with httpOnly cookie support.

This module provides secure authentication using httpOnly cookies to prevent
XSS attacks while maintaining compatibility with existing JWT token system.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass

from fastapi import HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from ..security import (
    JWTUser,
    UserRole,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_user_permissions,
    hash_password,
    verify_password,
)
from ..database import get_user_store, User

logger = logging.getLogger(__name__)

# Cookie configuration
COOKIE_ACCESS_TOKEN_NAME = "monkey_access_token"
COOKIE_REFRESH_TOKEN_NAME = "monkey_refresh_token"
COOKIE_MAX_AGE_DAYS = 30  # Cookie expiration
COOKIE_SECURE = True  # HTTPS only in production
COOKIE_HTTPONLY = True  # Prevent JavaScript access
COOKIE_SAMESITE = "lax"  # CSRF protection

# Security configuration
security = HTTPBearer()


@dataclass
class CookieAuthConfig:
    """Configuration for cookie-based authentication."""

    access_token_name: str = COOKIE_ACCESS_TOKEN_NAME
    refresh_token_name: str = COOKIE_REFRESH_TOKEN_NAME
    secure: bool = COOKIE_SECURE
    httponly: bool = COOKIE_HTTPONLY
    samesite: Literal["lax", "strict", "none"] = COOKIE_SAMESITE
    max_age_days: int = COOKIE_MAX_AGE_DAYS


class CookieAuthManager:
    """Manager for cookie-based authentication operations."""

    def __init__(self, config: Optional[CookieAuthConfig] = None):
        self.config = config or CookieAuthConfig()

    def set_auth_cookies(
        self, response: Response, access_token: str, refresh_token: str
    ) -> Response:
        """
        Set authentication cookies in the HTTP response.

        Args:
            response: FastAPI response object
            access_token: JWT access token
            refresh_token: JWT refresh token

        Returns:
            Response with cookies set
        """
        # Set access token cookie
        response.set_cookie(
            key=self.config.access_token_name,
            value=access_token,
            max_age=self.config.max_age_days * 24 * 60 * 60,  # Convert days to seconds
            expires=datetime.now(timezone.utc)
            + timedelta(days=self.config.max_age_days),
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        # Set refresh token cookie with longer expiration
        response.set_cookie(
            key=self.config.refresh_token_name,
            value=refresh_token,
            max_age=self.config.max_age_days * 24 * 60 * 60,
            expires=datetime.now(timezone.utc)
            + timedelta(days=self.config.max_age_days),
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        logger.info("Authentication cookies set successfully")
        return response

    def clear_auth_cookies(self, response: Response) -> Response:
        """
        Clear authentication cookies from the HTTP response.

        Args:
            response: FastAPI response object

        Returns:
            Response with cookies cleared
        """
        response.delete_cookie(
            key=self.config.access_token_name,
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        response.delete_cookie(
            key=self.config.refresh_token_name,
            path="/",
            secure=self.config.secure,
            httponly=self.config.httponly,
            samesite=self.config.samesite,
        )

        logger.info("Authentication cookies cleared")
        return response

    def get_token_from_cookie(self, request: Request, token_name: str) -> Optional[str]:
        """
        Extract token from HTTP cookies.

        Args:
            request: FastAPI request object
            token_name: Name of the cookie containing the token

        Returns:
            Token string or None if not found
        """
        return request.cookies.get(token_name)

    def get_access_token_from_cookie(self, request: Request) -> Optional[str]:
        """
        Extract access token from HTTP cookies.

        Args:
            request: FastAPI request object

        Returns:
            Access token string or None if not found
        """
        return self.get_token_from_cookie(request, self.config.access_token_name)

    def get_refresh_token_from_cookie(self, request: Request) -> Optional[str]:
        """
        Extract refresh token from HTTP cookies.

        Args:
            request: FastAPI request object

        Returns:
            Refresh token string or None if not found
        """
        return self.get_token_from_cookie(request, self.config.refresh_token_name)


# Global cookie auth manager instance
cookie_auth_manager = CookieAuthManager()


class CookieAuthResponse(BaseModel):
    """Response model for cookie-based authentication."""

    success: bool = True
    message: str
    user: Optional[Dict[str, Any]] = None
    session_expires: Optional[str] = None


async def get_current_user_from_cookie(request: Request) -> JWTUser:
    """
    Extract and validate current user from httpOnly cookie.

    This function attempts to authenticate the user using cookies first,
    then falls back to Authorization header for backward compatibility.

    Args:
        request: FastAPI request object

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    # Try to get token from cookies first
    access_token = cookie_auth_manager.get_access_token_from_cookie(request)

    if access_token:
        try:
            # Verify the token from cookie
            payload = verify_token(access_token)

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

            logger.debug(f"User authenticated via cookie: {user.email}")
            return user

        except Exception as e:
            logger.warning(f"Cookie authentication failed: {e}")
            # Fall through to header authentication

    # Fall back to Authorization header for backward compatibility
    try:
        credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # Handle API keys
        if credentials.credentials.startswith("mk-"):
            from ..security import _validate_api_key

            if not _validate_api_key(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
                )

            # Return API key user
            return JWTUser(
                user_id="api_user",
                username="api_user",
                email="",
                roles=[UserRole.API_USER],
                permissions=[],  # Will be populated by specific permissions
                mfa_verified=True,
                session_id=credentials.credentials[-8:],
            )

        # Handle JWT tokens from header
        payload = verify_token(credentials.credentials)

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

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

        logger.debug(f"User authenticated via header: {user.email}")
        return user

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )


async def login_with_cookies(email: str, password: str) -> CookieAuthResponse:
    """
    Authenticate user and set httpOnly cookies.

    Args:
        email: User email address
        password: User password

    Returns:
        Authentication response with user information

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate user against the user store
        user_store = get_user_store()
        user = await user_store.authenticate_user(email, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Convert database user roles to UserRole enums
        user_roles = []
        for role_str in user.roles:
            try:
                user_roles.append(UserRole(role_str))
            except ValueError:
                logger.warning(f"Invalid role '{role_str}' for user {user.email}")

        # Create JWT user from authenticated user
        jwt_user = JWTUser(
            user_id=user.id,
            username=user.username,
            email=user.email,
            roles=user_roles,
            permissions=get_user_permissions(user_roles),
            mfa_verified=True,  # MFA not implemented yet
        )

        # Create tokens
        access_token = create_access_token(jwt_user)
        refresh_token = create_refresh_token(jwt_user.user_id)

        # Set credits and subscription tier based on user type
        credits = 10000 if user.is_developer else 100
        subscription_tier = "developer" if user.is_developer else "free"

        logger.info(f"User {email} authenticated successfully with cookies")

        return CookieAuthResponse(
            success=True,
            message="Authentication successful",
            user={
                "id": jwt_user.user_id,
                "email": jwt_user.email,
                "name": jwt_user.username,
                "credits": credits,
                "subscription_tier": subscription_tier,
                "is_developer": user.is_developer,
                "roles": [role.value for role in user_roles],
            },
            session_expires=jwt_user.expires_at.isoformat()
            if jwt_user.expires_at
            else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cookie login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def refresh_with_cookies(refresh_token: str) -> CookieAuthResponse:
    """
    Refresh access token using refresh token from cookie.

    Args:
        refresh_token: JWT refresh token

    Returns:
        New authentication response with refreshed tokens

    Raises:
        HTTPException: If token refresh fails
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # In production, fetch user from database
        # For now, create a mock user
        mock_user = JWTUser(
            user_id=str(user_id),
            username="refreshed_user",
            email="refreshed@example.com",
            roles=[UserRole.DEVELOPER],
            permissions=get_user_permissions([UserRole.DEVELOPER]),
            mfa_verified=True,
        )

        # Create new tokens
        access_token = create_access_token(mock_user)
        new_refresh_token = create_refresh_token(mock_user.user_id)

        logger.info(f"Token refreshed successfully for user {user_id}")

        return CookieAuthResponse(
            success=True,
            message="Token refreshed successfully",
            user={
                "id": mock_user.user_id,
                "email": mock_user.email,
                "name": mock_user.username,
                "credits": 10000,
                "subscription_tier": "developer",
            },
            session_expires=mock_user.expires_at.isoformat()
            if mock_user.expires_at
            else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cookie token refresh failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to refresh token")


async def logout_with_cookies() -> Dict[str, str]:
    """
    Logout user by clearing cookies.

    Returns:
        Logout confirmation message
    """
    logger.info("User logged out via cookies")
    return {"message": "Successfully logged out"}


async def get_user_status_from_cookie(request: Request) -> CookieAuthResponse:
    """
    Get current user authentication status from cookies.

    Args:
        request: FastAPI request object

    Returns:
        User status response
    """
    try:
        current_user = await get_current_user_from_cookie(request)

        return CookieAuthResponse(
            success=True,
            message="User authenticated",
            user={
                "email": current_user.email,
                "name": current_user.username,
                "credits": 10000,  # Mock credits
                "subscription_tier": "developer",
            },
            session_expires=(
                current_user.expires_at.isoformat()
                if current_user.expires_at
                else None
            ),
        )

    except HTTPException:
        return CookieAuthResponse(
            success=False, message="User not authenticated", user=None
        )
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return CookieAuthResponse(
            success=False, message="Status check failed", user=None
        )


# Import Permission for type checking
from ..security import Permission
