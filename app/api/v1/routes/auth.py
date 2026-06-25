# app/api/v1/routes/auth.py
"""
Authentication Routes
Land Intelligence System
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth.auth_service import AuthService
from app.schemas.user_schema import UserCreate, UserLogin, TokenResponse, TokenRefresh, PasswordChange, UserResponse
from app.api.auth_dependencies import get_current_user_id, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account. Only admins can create non-viewer accounts."
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
):
    """
    Register a new user. Requires admin role for creating admin/client accounts.
    """
    from app.models.user import UserRole
    
    # Convert to dict
    data = user_data.model_dump(exclude_none=True)
    
    service = AuthService(db)
    
    try:
        user = await service.register_user(data)
        return service._user_to_response(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT tokens."
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and generate JWT tokens.
    """
    service = AuthService(db)
    
    try:
        return await service.login(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate new access token using refresh token."
)
async def refresh(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    result = await service.refresh_token(token_data.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result


@router.post(
    "/logout",
    summary="User logout",
    description="Invalidate current session/token."
)
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Logout user by invalidating token.
    """
    # TODO: Add token to blacklist in Redis
    return {"message": "Successfully logged out"}


@router.post(
    "/change-password",
    summary="Change password",
    description="Change user password."
)
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Change user password.
    """
    service = AuthService(db)
    
    try:
        success = await service.change_password(
            current_user_id,
            password_data.current_password,
            password_data.new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information."
)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get current user information.
    """
    service = AuthService(db)
    user = await service.get_user_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return service._user_to_response(user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update current user information."
)
async def update_current_user(
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update current user information.
    """
    service = AuthService(db)
    
    try:
        user = await service.update_user(current_user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return service._user_to_response(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )