# app/schemas/user_schema.py
"""
User Schemas
Land Intelligence System
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Fields shared by create, update, and response schemas."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user (admin-only endpoint)."""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.VIEWER
    parish_id: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserSelfUpdate(BaseModel):
    """
    Schema for PATCH /auth/me — fields a user is allowed to change on
    their own account.

    Critically, this schema does NOT include role, is_active, is_verified,
    or parish_id.  Accepting those from an arbitrary authenticated user
    would be a mass-assignment vulnerability (privilege escalation).
    Admins who need to change those fields must use an admin-only endpoint.
    """
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)


class UserUpdate(BaseModel):
    """
    Schema for admin-level user updates.
    Includes privileged fields that must never be reachable by non-admins.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    parish_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase):
    """Schema returned to clients — never includes hashed_password."""
    id: str
    role: UserRole
    parish_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema returned on successful login or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema for the change-password endpoint."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    items: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int