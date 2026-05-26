# app/api/middleware/authentication.py
"""
Authentication Middleware
Phase 1 — Section 2.5
Land Intelligence System
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from app.core.security import verify_token

logger = logging.getLogger(__name__)

# List of paths that don't require authentication
PUBLIC_PATHS = [
    "/health",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json"
]

security = HTTPBearer(auto_error=False)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates JWT Bearer tokens on protected routes.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request through authentication middleware.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response from next handler
        """
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
            return await call_next(request)
        
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning(f"Missing Authorization header for path: {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            # Parse Bearer token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
            
            # Validate token
            payload = verify_token(token)
            
            if not payload:
                logger.warning(f"Invalid token for path: {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Add user info to request state
            request.state.user = payload
            request.state.user_id = payload.get("sub")
            request.state.token = token
            
        except ValueError as e:
            logger.warning(f"Malformed Authorization header: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Proceed to next middleware/route
        return await call_next(request)


async def get_current_user(request: Request):
    """
    Dependency to get current authenticated user.
    
    Args:
        request: FastAPI request object
        
    Returns:
        dict: User information from token
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user


async def get_current_user_id(request: Request) -> str:
    """
    Dependency to get current authenticated user ID.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: User ID from token
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user_id