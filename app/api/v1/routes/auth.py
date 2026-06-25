# app/api/v1/routes/auth.py
"""
Authentication Routes
Land Intelligence System
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth.auth_service import AuthService
from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserSelfUpdate,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    UserResponse,
)
from app.api.auth_dependencies import get_current_user_id, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /auth/register  — admin-only
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account. Requires admin role.",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    service = AuthService(db)
    try:
        user = await service.register_user(user_data.model_dump(exclude_none=True))
        return service._user_to_response(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ---------------------------------------------------------------------------
# POST /auth/login  — public
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate and receive JWT access + refresh tokens.",
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    try:
        return await service.login(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# POST /auth/refresh  — public (carries its own refresh token)
# ---------------------------------------------------------------------------

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.refresh_token(token_data.refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


# ---------------------------------------------------------------------------
# POST /auth/logout  — authenticated
# ---------------------------------------------------------------------------

@router.post(
    "/logout",
    summary="User logout",
    description="Invalidate the current session token.",
)
async def logout(
    current_user_id: str = Depends(get_current_user_id),
):
    # TODO: implement Redis-backed token blacklist.
    # Until then the client must discard both tokens locally;
    # the access token remains technically valid until natural expiry.
    return {"message": "Successfully logged out"}


# ---------------------------------------------------------------------------
# POST /auth/change-password  — authenticated
# ---------------------------------------------------------------------------

@router.post(
    "/change-password",
    summary="Change password",
    description="Change the authenticated user's password.",
)
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    service = AuthService(db)
    try:
        success = await service.change_password(
            current_user_id,
            password_data.current_password,
            password_data.new_password,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password",
            )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ---------------------------------------------------------------------------
# GET /auth/me  — authenticated
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Return the authenticated user's profile.",
)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    service = AuthService(db)
    user = await service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return service._user_to_response(user)


# ---------------------------------------------------------------------------
# PATCH /auth/me  — authenticated
#
# Uses UserSelfUpdate instead of a raw dict, which means only full_name,
# email, and username are accepted.  role, is_active, is_verified, and
# parish_id are intentionally excluded — those require an admin endpoint.
# ---------------------------------------------------------------------------

@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description=(
        "Update the authenticated user's own profile. "
        "Only full_name, email, and username may be changed here. "
        "Role and account-status changes require an admin."
    ),
)
async def update_current_user(
    update_data: UserSelfUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    service = AuthService(db)
    try:
        # model_dump(exclude_none=True) so unset optional fields are not
        # written to the database (avoids overwriting existing values with None)
        user = await service.update_user(
            current_user_id,
            update_data.model_dump(exclude_none=True),
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return service._user_to_response(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))