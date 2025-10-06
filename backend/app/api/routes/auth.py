"""Authentication API routes."""

from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.api.middleware.rate_limiter import limiter
from app.core.config import settings
from app.services.token_blacklist import token_blacklist_service
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.crud.user import get_user_by_email, update_last_login
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Strict rate limit for login attempts
async def login(
    request: Request,  # Required for rate limiting
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return JWT tokens.

    Rate limited to 5 attempts per minute to prevent brute force attacks.

    Args:
        request: FastAPI request object (for rate limiting)
        credentials: Login credentials
        session: Database session

    Returns:
        TokenResponse with access and refresh tokens
    """
    # Get user by email
    user = await get_user_by_email(session, credentials.username)

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Update last login
    await update_last_login(session, user.id)

    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")  # Allow more frequent refresh attempts
async def refresh(
    req: Request,  # Required for rate limiting
    request: RefreshRequest,
    session: AsyncSession = Depends(get_session),
):
    """Refresh access token using refresh token.

    Rate limited to 10 attempts per minute.
    Checks if the refresh token is blacklisted before allowing refresh.

    Args:
        req: FastAPI request object (for rate limiting)
        request: Refresh token request
        session: Database session

    Returns:
        TokenResponse with new tokens

    Raises:
        HTTPException: If token is invalid, expired, or blacklisted
    """
    # Check if token is blacklisted (must be first to prevent use of invalidated tokens)
    is_blacklisted = await token_blacklist_service.is_blacklisted(
        request.refresh_token,
        token_type="refresh",
    )
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Load user from database
    from app.crud.user import get_user_by_id

    user = await get_user_by_id(session, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
):
    """Logout user by blacklisting their refresh token.

    Adds the refresh token to a Redis blacklist with TTL equal to token expiration.
    This ensures the token cannot be used to obtain new access tokens.

    Args:
        refresh_token: The refresh token to invalidate
        current_user: Current authenticated user (from access token)

    Raises:
        HTTPException: If token blacklisting fails
    """
    # Calculate TTL based on refresh token expiration (7 days default)
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # Blacklist the refresh token
    success = await token_blacklist_service.blacklist_token(
        token=refresh_token,
        expires_in_seconds=ttl_seconds,
        token_type="refresh",
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout. Please try again.",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse with user profile
    """
    return current_user
