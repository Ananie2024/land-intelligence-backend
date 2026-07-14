# app/api/v1/routes/users.py
"""
User Management Routes
Land Intelligence System

Admin-only endpoints for user management.
Regular users can update their own profile via /auth/me (PATCH).
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id, require_admin
from app.services.auth.auth_service import AuthService
from app.schemas.user_schema import (
    UserResponse,
    UserUpdate,
    UserListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /users  — list users (admin only)
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users",
    description="Return a paginated list of all active users with optional role filter.",
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by email or username"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    # Admin access required - enforced by dependency
    from app.models.user import UserRole
    from app.api.auth_dependencies import require_admin as admin_dep
    
    service = AuthService(db)
    users = await service.list_users(skip=(page - 1) * size, limit=size)
    
    # Create paginated response manually
    return {
        "items": [service._user_to_response(u) for u in users],
        "total": len(users),
        "page": page,
        "size": size,
        "pages": 1,
    }


# ---------------------------------------------------------------------------
# GET /users/{user_id}  — fetch single user
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user",
    description="Retrieve a single user by their UUID.",
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = AuthService(db)
    user = await service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found."
        )
    
    return service._user_to_response(user)


# ---------------------------------------------------------------------------
# PATCH /users/{user_id} — update user (admin only for privilege changes)
# ---------------------------------------------------------------------------

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Partially update a user's profile or account settings.",
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = AuthService(db)
    user = await service.update_user(user_id, payload.model_dump(exclude_none=True))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found."
        )
    
    return service._user_to_response(user)


# ---------------------------------------------------------------------------
# DELETE /users/{user_id} — soft delete user (admin only)
# ---------------------------------------------------------------------------

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Soft-delete a user (sets is_active=False).",
)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    service = AuthService(db)
    deleted = await service.delete_user(user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found."
        )
    
    from app.schemas.api_response import success_response
    return success_response(message=f"User '{user_id}' deleted successfully")