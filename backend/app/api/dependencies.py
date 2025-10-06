"""FastAPI dependencies for authentication and authorization."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.crud.catalog import get_upload_by_id
from app.crud.user import get_user_by_id
from app.db.session import get_session
from app.models.catalog_upload import CatalogUpload
from app.models.user import User, UserRole

# Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials
        session: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify JWT token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Load user from database
    user = await get_user_by_id(session, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        User object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


async def get_upload_owner(
    upload_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> CatalogUpload:
    """Get catalog upload and verify ownership.

    Args:
        upload_id: Upload ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        CatalogUpload object

    Raises:
        HTTPException: If upload not found or user doesn't have access
    """
    upload = await get_upload_by_id(session, upload_id)

    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    # Admin can access any upload, publisher only their own
    if current_user.role != UserRole.ADMIN and upload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return upload


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """Get current user if token is provided (optional authentication).

    Args:
        credentials: HTTP authorization credentials (optional)
        session: Database session

    Returns:
        User object or None if no token provided
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await get_user_by_id(session, int(user_id))
        return user
    except Exception:
        return None
