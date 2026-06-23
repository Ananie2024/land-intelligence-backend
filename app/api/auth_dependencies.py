"""
Authorization Dependencies
Land Intelligence System
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_data(
    request: Request,
    token: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Validate JWT token and return user data.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token.credentials)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.user = payload
    request.state.user_id = payload.get("sub")
    
    return payload


async def get_current_user_id(
    user_data: Dict[str, Any] = Depends(get_current_user_data)
) -> str:
    """
    Get authenticated user ID from token.
    """
    user_id = user_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    return str(user_id)


async def get_current_user_role(
    user_data: Dict[str, Any] = Depends(get_current_user_data)
) -> UserRole:
    """
    Get authenticated user role from token.
    """
    role = user_data.get("role")
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Role not found in token",
        )
    return UserRole(role)


async def get_current_user_from_db(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get full user object from database.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


# RBAC Dependencies

async def require_admin(
    user: User = Depends(get_current_user_from_db)
) -> User:
    """
    Require admin role.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return user


async def require_client_or_admin(
    user: User = Depends(get_current_user_from_db)
) -> User:
    """
    Require client or admin role.
    """
    if user.role not in [UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client or Admin role required",
        )
    return user


def require_role(allowed_roles: List[UserRole]):
    """
    Factory function to create role-specific authorization dependency.
    """
    async def check_role(
        user: User = Depends(get_current_user_from_db)
    ) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {[r.value for r in allowed_roles]}",
            )
        return user
    
    return check_role


async def require_parish_access(
    parish_id: str,
    user: User = Depends(get_current_user_from_db)
) -> bool:
    """
    Verify user has access to specific parish.
    Admins have access to all parishes.
    Clients can only access their assigned parish.
    """
    if user.role == UserRole.ADMIN:
        return True
    
    if user.role == UserRole.CLIENT:
        if str(user.parish_id) != parish_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this parish",
            )
        return True
    
    # Viewers have no write access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


async def prevent_viewer_access(
    user: User = Depends(get_current_user_from_db)
) -> User:
    """
    Prevent viewers from accessing write operations.
    """
    if user.role == UserRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot modify data",
        )
    return user