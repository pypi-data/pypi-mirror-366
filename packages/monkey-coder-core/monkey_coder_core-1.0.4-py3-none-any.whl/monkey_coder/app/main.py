"""
FastAPI main application for Monkey Coder Core Orchestration Engine.

This module provides the core FastAPI application with:
- /v1/execute endpoint for task routing & quantum execution
- /v1/billing/usage endpoint for metering
- Integration with SuperClaude, monkey1, and Gary8D systems
"""

import logging
import os
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import time
from pathlib import Path

from ..core.orchestrator import MultiAgentOrchestrator
from ..core.quantum_executor import QuantumExecutor
from ..core.persona_router import PersonaRouter
from ..providers import ProviderRegistry
from ..models import (
    ExecuteRequest,
    ExecuteResponse,
    UsageRequest,
    UsageResponse,
    TaskStatus,
    ExecutionError,
)
from ..security import (
    get_api_key,
    verify_permissions,
    get_current_user,
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
    JWTUser,
    UserRole,
    Permission,
    get_user_permissions,
)
from ..auth.cookie_auth import (
    get_current_user_from_cookie,
    login_with_cookies,
    refresh_with_cookies,
    logout_with_cookies,
    get_user_status_from_cookie,
    cookie_auth_manager,
    CookieAuthResponse,
)
from ..monitoring import MetricsCollector, BillingTracker
from ..database import run_migrations, User, get_user_store
from ..pricing import PricingMiddleware, load_pricing_from_file
from ..billing import StripeClient, BillingPortalSession
from ..feedback_collector import FeedbackCollector
from ..config.env_config import get_config, EnvironmentConfig
from ..auth import get_api_key_manager, APIKeyManager

# Import Railway-optimized logging first
from ..logging_utils import setup_logging, get_performance_logger, monitor_api_calls

# Configure Railway-optimized logging
setup_logging()
logger = logging.getLogger(__name__)
performance_logger = get_performance_logger("app_performance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting Monkey Coder Core Orchestration Engine...")

    # Initialize environment configuration
    try:
        config = get_config()
        app.state.config = config

        # Log configuration summary
        config_summary = config.get_config_summary()
        logger.info(f"Environment configuration loaded: {config_summary}")

        # Validate required configuration
        validation_result = config.validate_required_config()
        if validation_result["missing"]:
            logger.error(
                f"Missing required configuration: {validation_result['missing']}"
            )
        if validation_result["warnings"]:
            logger.warning(f"Configuration warnings: {validation_result['warnings']}")

    except Exception as e:
        logger.error(f"Failed to initialize environment configuration: {e}")
        # Continue startup with default configuration

    # Run database migrations
    try:
        await run_migrations()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        # Continue startup even if migrations fail (for development)

    import traceback

    # Initialize core components with health checks
    try:
        app.state.orchestrator = MultiAgentOrchestrator()
        logger.info("✅ MultiAgentOrchestrator initialized successfully")

        app.state.quantum_executor = QuantumExecutor()
        logger.info("✅ QuantumExecutor initialized successfully")

        app.state.persona_router = PersonaRouter()
        logger.info("✅ PersonaRouter initialized successfully")

        app.state.provider_registry = ProviderRegistry()
        logger.info("✅ ProviderRegistry initialized successfully")

        app.state.metrics_collector = MetricsCollector()
        logger.info("✅ MetricsCollector initialized successfully")

        app.state.billing_tracker = BillingTracker()
        logger.info("✅ BillingTracker initialized successfully")

        app.state.feedback_collector = FeedbackCollector()
        logger.info("✅ FeedbackCollector initialized successfully")

        app.state.api_key_manager = get_api_key_manager()
        logger.info("✅ APIKeyManager initialized successfully")

        # Initialize providers with timeout
        await app.state.provider_registry.initialize_all()
        logger.info("✅ All providers initialized successfully")

    except Exception as e:
        logger.error(f"❌ Component initialization failed: {e}")
        traceback.print_exc()
        # Continue startup even if some components fail
        # This allows the health endpoint to report component status

    logger.info("Orchestration engine started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Monkey Coder Core...")
    await app.state.provider_registry.cleanup_all()
    logger.info("Shutdown complete")


# Create FastAPI application with API docs under /api path
app = FastAPI(
    title="Monkey Coder Core",
    description="Python orchestration core for AI-powered code generation and analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Load pricing data from file (if exists) on startup
load_pricing_from_file()

# Initialize configuration for middleware setup
middleware_config = get_config()

# Add pricing middleware
enable_pricing = middleware_config._get_env_bool("ENABLE_PRICING_MIDDLEWARE", True)
app.add_middleware(PricingMiddleware, enabled=enable_pricing)

# Add other middleware with environment-aware configuration
allowed_origins = (
    ["*"]
    if middleware_config.environment != "production"
    else middleware_config._get_env("CORS_ORIGINS", "*").split(",")
)
allowed_hosts = (
    ["*"]
    if middleware_config.environment != "production"
    else middleware_config._get_env("TRUSTED_HOSTS", "*").split(",")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Add Sentry middleware for error tracking
app.add_middleware(SentryAsgiMiddleware)


# Add metrics collection middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect HTTP request metrics for Prometheus and Railway."""
    start_time = time.time()

    response = await call_next(request)

    # Calculate request duration
    duration = time.time() - start_time

    # Record metrics
    if hasattr(app.state, "metrics_collector"):
        app.state.metrics_collector.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration,
        )

    # Log performance data for Railway
    performance_logger.logger.info(
        "Request processed",
        extra={
            "extra_fields": {
                "metric_type": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        },
    )

    # Add performance headers
    response.headers["X-Process-Time"] = f"{duration:.4f}"

    return response


# Add font headers middleware
@app.middleware("http")
async def font_headers_middleware(request: Request, call_next):
    """Middleware to add proper headers for font files."""
    response = await call_next(request)

    # Check if this is a font file request
    path = request.url.path
    if path.endswith(('.woff2', '.woff', '.ttf', '.otf', '.eot')):
        # Set proper MIME type for font files
        if path.endswith('.woff2'):
            response.headers["Content-Type"] = "font/woff2"
        elif path.endswith('.woff'):
            response.headers["Content-Type"] = "font/woff"
        elif path.endswith('.ttf'):
            response.headers["Content-Type"] = "font/ttf"
        elif path.endswith('.otf'):
            response.headers["Content-Type"] = "font/otf"
        elif path.endswith('.eot'):
            response.headers["Content-Type"] = "application/vnd.ms-fontobject"

        # Add proper caching and CORS headers for fonts
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")
    components: Dict[str, str] = Field(..., description="Component status")


# Authentication Models
class LoginRequest(BaseModel):
    """Login request model."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Authentication response model."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: Dict[str, Any] = Field(..., description="User information")


class UserStatusResponse(BaseModel):
    """User status response model."""

    authenticated: bool = Field(..., description="User authentication status")
    user: Optional[Dict[str, Any]] = Field(
        None, description="User information if authenticated"
    )
    session_expires: Optional[str] = Field(
        None, description="Session expiration timestamp"
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., description="JWT refresh token")


class SignupRequest(BaseModel):
    """Signup request model."""

    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    plan: str = Field(default="hobby", description="Subscription plan")


# Root endpoint removed to allow Next.js static files to be served at root path


@app.get("/health", response_model=HealthResponse)
@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint optimized for Railway deployment.
    """
    from datetime import datetime
    import psutil

    # Get system metrics
    try:
        process = psutil.Process()
        memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        cpu_percent = process.cpu_percent()
    except Exception:
        memory_mb = 0
        cpu_percent = 0

    # Check component health
    components = {
        "orchestrator": "active" if hasattr(app.state, "orchestrator") else "inactive",
        "quantum_executor": (
            "active" if hasattr(app.state, "quantum_executor") else "inactive"
        ),
        "persona_router": (
            "active" if hasattr(app.state, "persona_router") else "inactive"
        ),
        "provider_registry": (
            "active" if hasattr(app.state, "provider_registry") else "inactive"
        ),
    }

    # Log health check for monitoring
    performance_logger.logger.info(
        "Health check performed",
        extra={
            "extra_fields": {
                "metric_type": "health_check",
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent,
                "components": components,
                "qwen_agent_available": "qwen_agent" in globals(),
            }
        },
    )

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        components=components,
    )


@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    if not hasattr(app.state, "metrics_collector"):
        return Response(
            content="# Metrics collector not initialized\n", media_type="text/plain"
        )

    metrics_data = app.state.metrics_collector.get_prometheus_metrics()
    return Response(content=metrics_data, media_type="text/plain")


# Authentication Endpoints
@app.post("/v1/auth/login", response_model=AuthResponse)
@app.post(
    "/api/auth/login", response_model=AuthResponse
)  # Frontend compatibility alias
async def login(request: LoginRequest) -> AuthResponse:
    """
    User login endpoint.

    Args:
        request: Login credentials (email and password)

    Returns:
        JWT tokens and user information
    """
    try:
        # Authenticate user against the user store
        user_store = get_user_store()
        user = await user_store.authenticate_user(request.email, request.password)

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
                # Handle any invalid roles gracefully
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
        credits = (
            10000 if user.is_developer else 100
        )  # Developer account gets more credits
        subscription_tier = "developer" if user.is_developer else "free"

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": jwt_user.user_id,
                "email": jwt_user.email,
                "name": jwt_user.username,
                "credits": credits,
                "subscription_tier": subscription_tier,
                "is_developer": user.is_developer,
                "roles": [role.value for role in user_roles],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/v1/auth/signup", response_model=AuthResponse)
@app.post(
    "/api/auth/signup", response_model=AuthResponse
)  # Frontend compatibility alias
async def signup(request: SignupRequest) -> AuthResponse:
    """
    User signup endpoint.

    Args:
        request: Signup credentials and information

    Returns:
        JWT tokens and user information for new user
    """
    try:
        # Get user store
        user_store = get_user_store()

        # Check if user already exists - need to use async method
        existing_user = await User.get_by_email(request.email.lower())
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        # Hash password before storing
        password_hash = hash_password(request.password)

        # Create new user with appropriate roles
        role_strings = ["api_user"]  # Use string roles that match UserRole enum values
        is_developer = False
        if request.plan == "pro":
            role_strings.append("developer")
            is_developer = True

        new_user = await user_store.create_user(
            username=request.name,
            email=request.email,
            password_hash=password_hash,  # Pass hashed password
            full_name=request.name,
            subscription_plan=request.plan,
            is_developer=is_developer,
            roles=role_strings,
        )

        # Convert string roles to UserRole enums
        user_roles = []
        for role_str in new_user.roles:
            try:
                user_roles.append(UserRole(role_str))
            except ValueError:
                logger.warning(
                    f"Invalid role '{role_str}' for new user {new_user.email}"
                )

        # Create JWT user
        jwt_user = JWTUser(
            user_id=str(new_user.id) if new_user.id else "new_user",
            username=new_user.username,
            email=new_user.email,
            roles=user_roles,
            permissions=get_user_permissions(user_roles),
            mfa_verified=True,
        )

        # Create tokens
        access_token = create_access_token(jwt_user)
        refresh_token = create_refresh_token(jwt_user.user_id)

        # Set credits and subscription tier based on plan
        credits = 10000 if request.plan == "pro" else 100

        logger.info(f"Created new user account: {request.email}")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": jwt_user.user_id,
                "email": jwt_user.email,
                "name": jwt_user.username,
                "credits": credits,
                "subscription_tier": request.plan,
                "is_developer": new_user.is_developer,
                "roles": [role.value for role in user_roles],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create account")


@app.get("/v1/auth/status", response_model=UserStatusResponse)
async def get_user_status(
    current_user: JWTUser = Depends(get_current_user),
) -> UserStatusResponse:
    """
    Get current user authentication status.

    Args:
        current_user: Current authenticated user

    Returns:
        User status and information
    """
    try:
        return UserStatusResponse(
            authenticated=True,
            user={
                "email": current_user.email,
                "name": current_user.username,
                "credits": 10000,  # Mock credits
                "subscription_tier": "developer",
            },
            session_expires=(
                current_user.expires_at.isoformat() if current_user.expires_at else None
            ),
        )

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user status")


@app.post("/v1/auth/logout")
async def logout(current_user: JWTUser = Depends(get_current_user)) -> Dict[str, str]:
    """
    User logout endpoint.

    Args:
        current_user: Current authenticated user

    Returns:
        Logout confirmation
    """
    try:
        # In production, you would invalidate the token in a blacklist
        logger.info(f"User {current_user.email} logged out")
        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


@app.post("/v1/auth/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest) -> AuthResponse:
    """
    Refresh JWT access token using refresh token.

    Args:
        request: Refresh token request

    Returns:
        New JWT tokens
    """
    try:
        from ..security import verify_token

        # Verify refresh token
        payload = verify_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Create new user object (in production, fetch from database)
        mock_user = JWTUser(
            user_id=str(user_id) if user_id else "refreshed_user",
            username="demo_user",
            email="demo@example.com",
            roles=[UserRole.DEVELOPER],
            permissions=get_user_permissions([UserRole.DEVELOPER]),
            mfa_verified=True,
        )

        # Create new tokens
        access_token = create_access_token(mock_user)
        new_refresh_token = create_refresh_token(mock_user.user_id)

        return AuthResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user={
                "id": mock_user.user_id,
                "email": mock_user.email,
                "name": mock_user.username,
                "credits": 10000,
                "subscription_tier": "developer",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to refresh token")


# Cookie-based Authentication Endpoints (Enhanced Security)

@app.post("/v1/auth/login/cookie", response_model=CookieAuthResponse)
async def login_with_cookie_endpoint(request: LoginRequest) -> Response:
    """
    Enhanced user login endpoint with httpOnly cookies.

    This endpoint provides secure authentication using httpOnly cookies
    to prevent XSS attacks while maintaining backward compatibility.

    Args:
        request: Login credentials (email and password)

    Returns:
        CookieAuthResponse with user information and session details
    """
    try:
        # Authenticate user and get response
        auth_response = await login_with_cookies(request.email, request.password)

        # Create response with cookies
        response = JSONResponse(
            content=auth_response.model_dump(),
            status_code=200,
        )

        # Set httpOnly cookies with tokens
        if auth_response.success:
            # Create new tokens for cookie storage
            user_store = get_user_store()
            user = await user_store.authenticate_user(request.email, request.password)

            if user:
                # Convert database user roles to UserRole enums
                user_roles = []
                for role_str in user.roles:
                    try:
                        user_roles.append(UserRole(role_str))
                    except ValueError:
                        logger.warning(f"Invalid role '{role_str}' for user {user.email}")

                # Create JWT user from authenticated user
                jwt_user = JWTUser(
                    user_id=str(user.id) if user.id else "unknown_user",
                    username=user.username,
                    email=user.email,
                    roles=user_roles,
                    permissions=get_user_permissions(user_roles),
                    mfa_verified=True,
                )

                # Create tokens
                access_token = create_access_token(jwt_user)
                refresh_token = create_refresh_token(jwt_user.user_id)

                # Set httpOnly cookies
                cookie_auth_manager.set_auth_cookies(response, access_token, refresh_token)

                # Log successful authentication
                logger.info(f"User {request.email} authenticated successfully with httpOnly cookies")

                # Set security headers
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cookie login endpoint failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@app.post("/v1/auth/refresh/cookie", response_model=CookieAuthResponse)
async def refresh_with_cookie_endpoint(request: Request) -> Response:
    """
    Refresh access token using httpOnly cookies.

    This endpoint securely refreshes the access token using the refresh token
    stored in httpOnly cookies, preventing token exposure to JavaScript.

    Args:
        request: FastAPI request object containing cookies

    Returns:
        CookieAuthResponse with new tokens and user information
    """
    try:
        # Get refresh token from cookie
        refresh_token = cookie_auth_manager.get_refresh_token_from_cookie(request)
        if not refresh_token:
            raise HTTPException(
                status_code=401, detail="No refresh token found in cookies"
            )

        # Refresh tokens
        auth_response = await refresh_with_cookies(refresh_token)

        # Create response with new cookies
        response = JSONResponse(
            content=auth_response.model_dump(),
            status_code=200,
        )

        # Set new httpOnly cookies
        if auth_response.success:
            # Create new user object for token generation
            mock_user = JWTUser(
                user_id="refreshed_user",
                username="refreshed_user",
                email="refreshed@example.com",
                roles=[UserRole.DEVELOPER],
                permissions=get_user_permissions([UserRole.DEVELOPER]),
                mfa_verified=True,
            )

            # Create new tokens
            access_token = create_access_token(mock_user)
            new_refresh_token = create_refresh_token(mock_user.user_id)

            # Set new httpOnly cookies
            cookie_auth_manager.set_auth_cookies(response, access_token, new_refresh_token)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cookie refresh endpoint failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to refresh token")


@app.post("/v1/auth/logout/cookie")
async def logout_with_cookie_endpoint(request: Request) -> Response:
    """
    Secure logout endpoint that clears httpOnly cookies.

    This endpoint clears all authentication cookies to securely
    log out the user and prevent session hijacking.

    Args:
        request: FastAPI request object

    Returns:
        Logout confirmation message
    """
    try:
        # Perform logout logic
        logout_result = await logout_with_cookies()

        # Create response and clear cookies
        response = JSONResponse(content=logout_result, status_code=200)
        cookie_auth_manager.clear_auth_cookies(response)

        return response

    except Exception as e:
        logger.error(f"Cookie logout endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


@app.get("/v1/auth/status/cookie", response_model=CookieAuthResponse)
async def get_user_status_with_cookie(request: Request) -> CookieAuthResponse:
    """
    Get user authentication status using httpOnly cookies.

    This endpoint checks the user's authentication status using
    secure httpOnly cookies without exposing tokens to JavaScript.

    Args:
        request: FastAPI request object containing cookies

    Returns:
        CookieAuthResponse with user status information
    """
    try:
        return await get_user_status_from_cookie(request)

    except Exception as e:
        logger.error(f"Cookie status endpoint failed: {str(e)}")
        return CookieAuthResponse(
            success=False, message="Status check failed", user=None
        )


# Enhanced authentication dependency that supports both cookies and headers
async def get_current_user_enhanced(request: Request) -> JWTUser:
    """
    Enhanced authentication dependency supporting both cookies and headers.

    This function provides unified authentication that:
    1. First attempts cookie-based authentication (more secure)
    2. Falls back to Authorization header (backward compatibility)
    3. Handles API keys seamlessly

    Args:
        request: FastAPI request object

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    return await get_current_user_from_cookie(request)


@app.post("/v1/execute", response_model=ExecuteResponse)
async def execute_task(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
) -> ExecuteResponse:
    """
    Main task execution endpoint with routing & quantum execution.

    This endpoint:
    1. Routes tasks through SuperClaude slash-command & persona router
    2. Orchestrates execution via monkey1 multi-agent system
    3. Executes tasks using Gary8D functional-quantum executor
    4. Tracks usage and billing metrics

    Args:
        request: Task execution request
        background_tasks: FastAPI background tasks
        api_key: API key for authentication

    Returns:
        ExecuteResponse with task results and metadata

    Raises:
        HTTPException: If task execution fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "execute")

        # Start metrics collection
        execution_id = app.state.metrics_collector.start_execution(request)

        # Route through persona system (SuperClaude integration)
        persona_context = await app.state.persona_router.route_request(request)

        # Execute through multi-agent orchestrator (monkey1 integration)
        orchestration_result = await app.state.orchestrator.orchestrate(
            request, persona_context
        )

        # Execute via quantum executor (Gary8D integration)
        execution_result = await app.state.quantum_executor.execute(
            orchestration_result, parallel_futures=True
        )

        # Prepare response
        response = ExecuteResponse(
            execution_id=execution_id,
            task_id=request.task_id,
            status=TaskStatus.COMPLETED,
            result=execution_result.result,
            usage=execution_result.usage,
            execution_time=execution_result.execution_time,
        )

        # Track billing in background
        background_tasks.add_task(
            app.state.billing_tracker.track_usage, api_key, execution_result.usage
        )

        # Complete metrics collection
        app.state.metrics_collector.complete_execution(
            execution_id=execution_id,
            response=response,
            error=None,
            completed_at=datetime.utcnow()
        )

        return response

    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")

        # Track error metrics
        if "execution_id" in locals():
            app.state.metrics_collector.record_error(execution_id, str(e))

        # Return appropriate error response
        if isinstance(e, ExecutionError):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/v1/billing/usage", response_model=UsageResponse)
async def get_usage_metrics(
    request: UsageRequest = Depends(),
    api_key: str = Depends(get_api_key),
) -> UsageResponse:
    """
    Billing and usage metrics endpoint.

    Provides detailed usage statistics including:
    - Token consumption by provider
    - Execution counts and durations
    - Cost breakdowns
    - Rate limiting status

    Args:
        request: Usage request parameters
        api_key: API key for authentication

    Returns:
        UsageResponse with detailed usage metrics

    Raises:
        HTTPException: If metrics retrieval fails
    """
    try:
        # Verify permissions
        await verify_permissions(api_key, "billing:read")

        # Get usage data from billing tracker
        usage_data = await app.state.billing_tracker.get_usage(
            api_key=api_key,
            start_date=request.start_date,
            end_date=request.end_date,
            granularity=request.granularity,
        )

        return UsageResponse(
            api_key_hash=usage_data.api_key_hash,
            period=usage_data.period,
            total_requests=usage_data.total_requests,
            total_tokens=usage_data.total_tokens,
            total_cost=usage_data.total_cost,
            provider_breakdown=usage_data.provider_breakdown,
            execution_stats=usage_data.execution_stats,
            rate_limit_status=usage_data.rate_limit_status,
        )

    except Exception as e:
        logger.error(f"Usage metrics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage metrics")


@app.post("/v1/billing/portal", response_model=BillingPortalSession)
async def create_billing_portal_session(
    api_key: str = Depends(get_api_key),
    return_url: str = "https://yourdomain.com/billing",
) -> BillingPortalSession:
    """
    Create a Stripe billing portal session.

    This endpoint creates a billing portal session that allows customers
    to manage their billing information, view invoices, and update payment methods.

    Args:
        api_key: API key for authentication
        return_url: URL to redirect to after session ends

    Returns:
        BillingPortalSession: Session information including URL

    Raises:
        HTTPException: If session creation fails
    """
    from ..database.models import BillingCustomer
    import hashlib

    try:
        # Verify permissions
        await verify_permissions(api_key, "billing:manage")

        # Hash API key to find customer
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]

        # Get billing customer
        billing_customer = await BillingCustomer.get_by_api_key_hash(api_key_hash)
        if not billing_customer:
            raise HTTPException(
                status_code=404,
                detail="No billing customer found. Please contact support to set up billing.",
            )

        # Create Stripe client and billing portal session
        stripe_client = StripeClient()
        session_url = stripe_client.create_billing_portal_session(
            customer_id=billing_customer.stripe_customer_id, return_url=return_url
        )

        return BillingPortalSession(
            session_url=session_url, customer_id=billing_customer.stripe_customer_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing portal session: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create billing portal session"
        )


@app.get("/v1/providers", response_model=Dict[str, Any])
async def list_providers(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    List available AI providers and their status.

    Returns information about supported providers:
    - OpenAI (GPT models)
    - Anthropic (Claude models)
    - Google (Gemini models)
    - Qwen (Qwen Coder models)

    Args:
        api_key: API key for authentication

    Returns:
        Dictionary with provider information and status
    """
    try:
        await verify_permissions(api_key, "providers:read")

        providers = app.state.provider_registry.get_all_providers()
        return {"providers": providers, "count": len(providers), "status": "active"}

    except Exception as e:
        logger.error(f"Provider listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list providers")


@app.get("/v1/models", response_model=Dict[str, Any])
async def list_models(
    provider: Optional[str] = None,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    List available AI models by provider.

    Args:
        provider: Optional provider filter (openai, anthropic, google, qwen)
        api_key: API key for authentication

    Returns:
        Dictionary with model information by provider
    """
    try:
        await verify_permissions(api_key, "models:read")

        models = await app.state.provider_registry.get_available_models(provider)
        return {
            "models": models,
            "provider_filter": provider,
            "count": sum(len(models[p]) for p in models),
        }

    except Exception as e:
        logger.error(f"Model listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list models")


@app.post("/v1/router/debug", response_model=Dict[str, Any])
async def debug_routing(
    request: ExecuteRequest,
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Debug routing decisions for a given request.

    This endpoint provides detailed information about how the AdvancedRouter
    would route a given request, including:
    - Selected model and provider
    - Chosen persona
    - Complexity, context, and capability scores
    - Reasoning behind the decision
    - Available alternatives

    Args:
        request: The execution request to analyze
        api_key: API key for authentication

    Returns:
        Detailed routing debug information
    """
    try:
        await verify_permissions(api_key, "router:debug")

        # Get detailed routing debug information
        debug_info = app.state.persona_router.get_routing_debug_info(request)

        return {
            "debug_info": debug_info,
            "request_summary": {
                "task_type": request.task_type.value,
                "prompt_length": len(request.prompt),
                "has_files": bool(request.files),
                "file_count": len(request.files) if request.files else 0,
            },
            "personas_available": app.state.persona_router.get_available_personas(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Router debug failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to generate routing debug info"
        )


@app.get("/v1/capabilities", response_model=Dict[str, Any])
async def get_system_capabilities(
    api_key: str = Depends(get_api_key),
) -> Dict[str, Any]:
    """
    Get comprehensive system capabilities information.

    This endpoint provides detailed information about:
    - Environment configuration status
    - Persona validation capabilities
    - Orchestration strategies and patterns
    - Available providers and models
    - System health and performance metrics

    Args:
        api_key: API key for authentication

    Returns:
        Comprehensive system capabilities information
    """
    try:
        await verify_permissions(api_key, "system:read")

        # Get environment configuration summary
        config_summary = None
        if hasattr(app.state, "config"):
            config_summary = app.state.config.get_config_summary()

        # Get persona validation stats
        validation_stats = app.state.persona_router.get_validation_stats()

        # Get orchestration capabilities
        orchestration_caps = app.state.orchestrator.get_orchestration_capabilities()

        # Get provider information
        providers = app.state.provider_registry.get_all_providers()

        return {
            "system_info": {
                "version": "1.0.0",
                "environment": (
                    config_summary.get("environment") if config_summary else "unknown"
                ),
                "debug_mode": config_summary.get("debug") if config_summary else False,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "environment_configuration": {
                "status": "configured" if config_summary else "default",
                "summary": config_summary,
                "validation_warnings": (
                    [] if config_summary else ["Using default configuration"]
                ),
            },
            "persona_validation": {
                "enhanced_validation": True,
                "single_word_support": True,
                "edge_case_handling": True,
                "capabilities": validation_stats,
            },
            "orchestration": {
                "enhanced_patterns": True,
                "multi_strategy_support": True,
                "intelligent_coordination": True,
                "capabilities": orchestration_caps,
            },
            "providers": {
                "total_providers": len(providers),
                "active_providers": [
                    p["name"] for p in providers if p.get("status") == "active"
                ],
                "provider_details": providers,
            },
            "features": [
                "environment_configuration_management",
                "persona_aware_routing_with_validation",
                "single_word_input_enhancement",
                "edge_case_prompt_handling",
                "multi_strategy_orchestration",
                "sequential_agent_coordination",
                "parallel_task_execution",
                "quantum_inspired_processing",
                "hybrid_orchestration_strategies",
                "intelligent_agent_handoff",
                "comprehensive_error_handling",
                "production_ready_deployment",
            ],
            "recent_enhancements": [
                {
                    "feature": "Environment Configuration",
                    "description": "Centralized environment variable management with validation",
                    "status": "implemented",
                },
                {
                    "feature": "Persona Validation",
                    "description": "Enhanced validation for single-word inputs and edge cases",
                    "status": "implemented",
                },
                {
                    "feature": "Orchestration Patterns",
                    "description": "Advanced orchestration strategies from reference projects",
                    "status": "implemented",
                },
                {
                    "feature": "Frontend Serving",
                    "description": "Improved static file serving with fallback handling",
                    "status": "implemented",
                },
            ],
        }

    except Exception as e:
        logger.error(f"Capabilities retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve system capabilities"
        )


# API Key Management Endpoints


class APIKeyCreateRequest(BaseModel):
    """Request model for creating new API keys."""

    name: str = Field(..., description="Human-readable name for the API key")
    description: str = Field("", description="Description of the key's purpose")
    permissions: Optional[List[str]] = Field(
        None, description="List of permissions (default: basic permissions)"
    )
    expires_days: Optional[int] = Field(
        None, description="Number of days until expiration (None = no expiration)"
    )


class APIKeyResponse(BaseModel):
    """Response model for API key operations."""

    key: Optional[str] = Field(
        None, description="The generated API key (only returned on creation)"
    )
    key_id: str = Field(..., description="Unique key identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Key description")
    status: str = Field(..., description="Key status")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")
    last_used: Optional[str] = Field(None, description="Last used timestamp")
    usage_count: int = Field(..., description="Number of times used")
    permissions: List[str] = Field(..., description="Assigned permissions")


@app.post("/v1/auth/keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: JWTUser = Depends(get_current_user),
) -> APIKeyResponse:
    """
    Create a new API key.

    This endpoint allows authenticated users to generate new API keys
    for programmatic access to the API.

    Args:
        request: API key creation request
        current_user: Current authenticated user

    Returns:
        APIKeyResponse: The created API key information including the actual key

    Raises:
        HTTPException: If key creation fails
    """
    try:
        # Check permissions
        if UserRole.ADMIN not in current_user.roles and UserRole.DEVELOPER not in current_user.roles:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to create API keys"
            )

        # Create the API key
        key_data = app.state.api_key_manager.generate_api_key(
            name=request.name,
            description=request.description,
            permissions=request.permissions,
            expires_days=request.expires_days,
        )

        logger.info(f"Created API key '{request.name}' for user {current_user.user_id}")

        return APIKeyResponse(
            key=key_data["key"],  # Only returned on creation
            key_id=key_data["key_id"],
            name=key_data["name"],
            description=key_data["description"],
            status=key_data["status"],
            created_at=key_data["created_at"],
            expires_at=key_data["expires_at"] if "expires_at" in key_data else None,
            last_used=None,
            usage_count=0,
            permissions=key_data["permissions"],
        )

    except Exception as e:
        logger.error(f"API key creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@app.post("/v1/auth/keys/dev", response_model=APIKeyResponse)
async def create_development_api_key() -> APIKeyResponse:
    """
    Create a development API key for testing (no authentication required).

    This endpoint is for development and testing purposes only.
    It creates an API key without requiring authentication.

    Returns:
        APIKeyResponse: The created development API key

    Raises:
        HTTPException: If key creation fails
    """
    try:
        # Create a development API key
        key_data = app.state.api_key_manager.generate_api_key(
            name=f"Development Key {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description="Development/testing API key created via /v1/auth/keys/dev endpoint",
            permissions=["*"],  # Full permissions for development
            expires_days=30,  # 30 days expiration
            metadata={"type": "development", "created_via": "dev_endpoint"},
        )

        logger.info(f"Created development API key: {key_data['key'][:15]}...")

        return APIKeyResponse(
            key=key_data["key"],
            key_id=key_data["key_id"],
            name=key_data["name"],
            description=key_data["description"],
            status=key_data["status"],
            created_at=key_data["created_at"],
            expires_at=key_data.get("expires_at"),
            last_used=None,
            usage_count=0,
            permissions=key_data["permissions"],
        )

    except Exception as e:
        logger.error(f"Development API key creation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create development API key"
        )


@app.get("/v1/auth/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: JWTUser = Depends(get_current_user),
) -> List[APIKeyResponse]:
    """
    List all API keys for the current user.

    Args:
        current_user: Current authenticated user

    Returns:
        List of API key information (without the actual keys)

    Raises:
        HTTPException: If listing fails
    """
    try:
        # Check permissions
        if UserRole.ADMIN not in current_user.roles and UserRole.DEVELOPER not in current_user.roles:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to create API keys"
            )

        # Get all API keys
        keys = app.state.api_key_manager.list_api_keys()

        # Convert to response format
        response_keys = []
        for key_data in keys:
            response_keys.append(
                APIKeyResponse(
                    key=None,  # Never return actual keys in list
                    key_id=key_data["key_id"],
                    name=key_data["name"],
                    description=key_data["description"],
                    status=key_data["status"],
                    created_at=key_data["created_at"],
                    expires_at=key_data["expires_at"],
                    last_used=key_data["last_used"],
                    usage_count=key_data["usage_count"],
                    permissions=key_data["permissions"],
                )
            )

        return response_keys

    except Exception as e:
        logger.error(f"API key listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@app.delete("/v1/auth/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: JWTUser = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Revoke an API key.

    Args:
        key_id: The ID of the API key to revoke
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If revocation fails or key not found
    """
    try:
        # Check permissions
        if UserRole.ADMIN not in current_user.roles and UserRole.DEVELOPER not in current_user.roles:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to revoke API keys"
            )

        # Revoke the key
        success = app.state.api_key_manager.revoke_api_key(key_id)

        if not success:
            raise HTTPException(status_code=404, detail="API key not found")

        logger.info(f"Revoked API key {key_id} by user {current_user.user_id}")

        return {"message": "API key revoked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key revocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to revoke API key")


@app.get("/v1/auth/keys/stats", response_model=Dict[str, Any])
async def get_api_key_stats(
    current_user: JWTUser = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get API key usage statistics.

    Args:
        current_user: Current authenticated user

    Returns:
        Dictionary containing API key statistics

    Raises:
        HTTPException: If user lacks permissions
    """
    try:
        # Check permissions
        if UserRole.ADMIN not in current_user.roles:
            raise HTTPException(
                status_code=403,
                detail="Admin permissions required for API key statistics",
            )

        stats = app.state.api_key_manager.get_stats()

        return {"statistics": stats, "timestamp": datetime.utcnow().isoformat()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key stats retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve API key statistics"
        )


# Error handlers
@app.exception_handler(ExecutionError)
async def execution_error_handler(request, exc: ExecutionError):
    """Handle execution errors with proper error response."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "ExecutionError",
            "message": str(exc),
            "type": exc.__class__.__name__,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


def create_app() -> FastAPI:
    """
    Application factory function.

    Returns:
        Configured FastAPI application instance
    """
    return app


# Mount static files for Next.js frontend (must be after all API routes)
# Try multiple possible locations for static files
static_dir_options = [
    Path(__file__).parent.parent.parent.parent
    / "packages"
    / "web"
    / "out",  # Unified Dockerfile location
    Path(__file__).parent.parent.parent.parent / "web" / "out",  # Legacy location
    Path("/app/packages/web/out"),  # Absolute path in Docker
    Path("/app/web/out"),  # Alternative absolute path
]

static_dir = None
for option in static_dir_options:
    if option.exists():
        static_dir = option
        break

if static_dir:
    # Configure MIME types for fonts before mounting
    import mimetypes
    mimetypes.add_type('font/woff2', '.woff2')
    mimetypes.add_type('font/woff', '.woff')
    mimetypes.add_type('font/ttf', '.ttf')
    mimetypes.add_type('font/otf', '.otf')
    mimetypes.add_type('application/vnd.ms-fontobject', '.eot')

    # Mount static files with fallback to index.html for SPA routing
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"✅ Static files served from: {static_dir} with proper font MIME types")
else:
    logger.warning(
        f"❌ Static directory not found in any of: {[str(p) for p in static_dir_options]}. Frontend will not be served."
    )

    # Add fallback route when static files are not available
    @app.get("/")
    async def frontend_fallback():
        """Fallback route when frontend static files are not available."""
        return HTMLResponse(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Monkey Coder API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
                .api-link { color: #007cba; text-decoration: none; }
                .api-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🐒 Monkey Coder API</h1>
                <p>FastAPI backend is running successfully!</p>
            </div>

            <h2>API Documentation</h2>
            <ul>
                <li><a href="/api/docs" class="api-link">Interactive API Documentation (Swagger)</a></li>
                <li><a href="/api/redoc" class="api-link">ReDoc API Documentation</a></li>
                <li><a href="/health" class="api-link">Health Check</a></li>
                <li><a href="/metrics" class="api-link">Prometheus Metrics</a></li>
            </ul>

            <h2>Available Endpoints</h2>
            <ul>
                <li><code>POST /v1/auth/login</code> - User authentication</li>
                <li><code>GET /v1/auth/status</code> - Authentication status</li>
                <li><code>POST /v1/auth/keys/dev</code> - <strong>Create development API key</strong> 🔑</li>
                <li><code>GET /v1/auth/keys</code> - List API keys</li>
                <li><code>POST /v1/execute</code> - Task execution</li>
                <li><code>GET /v1/billing/usage</code> - Usage metrics</li>
                <li><code>GET /v1/providers</code> - List AI providers</li>
                <li><code>GET /v1/models</code> - List available models</li>
                <li><code>GET /v1/capabilities</code> - System capabilities and features</li>
            </ul>

            <h2>🚀 Quick Start</h2>
            <p><strong>Get an API key for testing:</strong></p>
            <pre><code>curl -X POST https://your-domain.railway.app/v1/auth/keys/dev</code></pre>
            <p><strong>Then use it to test the API:</strong></p>
            <pre><code>curl -H "Authorization: Bearer mk-YOUR_KEY" https://your-domain.railway.app/v1/auth/status</code></pre>

            <p><em>Frontend static files not found. API endpoints are fully functional.</em></p>
        </body>
        </html>
        """
        )


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "monkey_coder.app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True,
    )
