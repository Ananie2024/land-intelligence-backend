"""
Security & Authentication Dependencies
Land Intelligence System
"""

import logging
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

from app.core.security import verify_token

logger = logging.getLogger(__name__)

# Security scheme for Swagger/OpenAPI
reusable_oauth2 = HTTPBearer(auto_error=False)


async def get_current_user_data(
    request: Request,
    token: Optional[HTTPAuthorizationCredentials] = Depends(reusable_oauth2)
) -> Dict[str, Any]:
    """
    Dependency to validate JWT token and return user data.
    Replaces AuthenticationMiddleware by performing validation
    as a FastAPI dependency.
    """
    if not token:
        logger.warning(
            f"Missing authentication token for path: {request.url.path}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token.credentials)

    if not payload:
        logger.warning(
            f"Invalid or expired token for path: {request.url.path}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attach to request state for backward compatibility if needed,
    # but preferred way is to use the return value of this dependency.
    request.state.user = payload
    request.state.user_id = payload.get("sub")

    return payload


async def get_current_user_id(
    user_data: Dict[str, Any] = Depends(get_current_user_data)
) -> str:
    """
    Dependency to retrieve authenticated user ID.
    """
    user_id = user_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    return str(user_id)
