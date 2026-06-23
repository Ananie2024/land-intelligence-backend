# app/api/middleware/authentication.py

"""
Authentication Middleware
Phase 1 — Section 2.5
Land Intelligence System
"""

import logging

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.security import verify_token

logger = logging.getLogger(__name__)


PUBLIC_PATHS = {
    "/health",
    "/api/v1/health",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",

    # Optional fallbacks
    "/docs",
    "/redoc",
    "/openapi.json",
}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates JWT Bearer tokens
    on protected routes.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public endpoints
        if path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning(
                f"Missing Authorization header for path: {path}"
            )

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Missing authentication token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            parts = auth_header.split()

            if len(parts) != 2:
                raise ValueError(
                    "Authorization header must contain scheme and token"
                )

            scheme, token = parts

            if scheme.lower() != "bearer":
                raise ValueError(
                    "Invalid authentication scheme"
                )

            payload = verify_token(token)

            if not payload:
                logger.warning(
                    f"Invalid token for path: {path}"
                )

                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Invalid or expired token"
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

            request.state.user = payload
            request.state.user_id = payload.get("sub")
            request.state.token = token

        except ValueError as e:
            logger.warning(
                f"Malformed Authorization header: {e}"
            )

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Invalid authorization header format"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        except Exception as e:
            logger.exception(
                f"Authentication error: {e}"
            )

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Authentication failed"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)


async def get_current_user(request: Request):
    """
    Dependency to retrieve authenticated user.
    """

    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return request.state.user


async def get_current_user_id(request: Request) -> str:
    """
    Dependency to retrieve authenticated user ID.
    """

    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return request.state.user_id