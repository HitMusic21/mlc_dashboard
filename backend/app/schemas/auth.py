"""Pydantic schemas for Auth API endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request schema for POST /auth/login."""

    username: EmailStr = Field(description="User email address")
    password: str = Field(min_length=1, description="User password")


class RefreshRequest(BaseModel):
    """Request schema for POST /auth/refresh."""

    refresh_token: str = Field(min_length=1, description="Refresh token")


class TokenResponse(BaseModel):
    """Response schema for login and refresh endpoints."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(ge=1, description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """Response schema for GET /auth/me."""

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
