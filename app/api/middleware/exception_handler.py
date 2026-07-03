# app/api/middleware/exception_handler.py
"""
Centralized Global Exception Handler
Land Intelligence System
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from jwt import InvalidTokenError

from app.schemas.api_response import error_response

logger = logging.getLogger(__name__)


def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity).
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append({
            "field": field,
            "message": error.get("msg", "Validation failed"),
            "code": error.get("type", "validation_error")
        })

    logger.warning(
        "Request validation error occurred",
        extra={
            "path": request.url.path,
            "errors": errors,
        }
    )

    response = error_response(
        message="Validation error",
        errors=errors
    )

    return JSONResponse(
        status_code=422,
        content=response
    )


def _authentication_error(request: Request, message: str) -> JSONResponse:
    """
    Handle authentication errors (401 Unauthorized).
    """
    response = error_response(
        message=message or "Authentication required",
        errors=[{
            "field": "token",
            "message": message,
            "code": "authentication_error"
        }]
    )

    return JSONResponse(
        status_code=401,
        content=response,
        headers={"WWW-Authenticate": "Bearer"}
    )


def _authorization_error(request: Request, message: str) -> JSONResponse:
    """
    Handle authorization errors (403 Forbidden).
    """
    response = error_response(
        message=message or "Insufficient permissions",
        errors=[{
            "field": "permissions",
            "message": message,
            "code": "authorization_error"
        }]
    )

    return JSONResponse(
        status_code=403,
        content=response
    )


def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    """
    status_code = exc.status_code
    detail = exc.detail

    logger.warning(
        "HTTP exception occurred",
        extra={
            "path": request.url.path,
            "status_code": status_code,
            "detail": detail,
        }
    )

    # Categorize based on status code
    if status_code == 401:
        return _authentication_error(request, detail)
    elif status_code == 403:
        return _authorization_error(request, detail)
    elif status_code == 404:
        response = error_response(
            message=detail or "Resource not found",
            errors=[{
                "field": "resource",
                "message": detail,
                "code": "not_found"
            }]
        )
        return JSONResponse(status_code=404, content=response)
    elif status_code == 409:
        response = error_response(
            message=detail or "Conflict",
            errors=[{
                "field": "conflict",
                "message": detail,
                "code": "conflict"
            }]
        )
        return JSONResponse(status_code=409, content=response)
    elif status_code == 422:
        response = error_response(
            message=detail or "Validation error",
            errors=[{
                "field": "validation",
                "message": str(detail),
                "code": "validation_error"
            }]
        )
        return JSONResponse(status_code=422, content=response)
    else:
        response = error_response(
            message=detail or "HTTP error occurred",
            errors=[{
                "message": str(detail),
                "code": f"http_{status_code}"
            }]
        )
        return JSONResponse(status_code=status_code, content=response)


def _database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database errors (500 Internal Server Error).
    """
    logger.error(
        "Database error occurred",
        extra={
            "path": request.url.path,
            "error": str(exc),
        },
        exc_info=True
    )

    response = error_response(
        message="Database operation failed",
        errors=[{
            "field": "database",
            "message": "An internal database error occurred",
            "code": "database_error"
        }]
    )

    return JSONResponse(status_code=500, content=response)


def _business_error(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handle business logic errors (400 Bad Request).
    """
    response = error_response(
        message=str(exc) or "Business logic error",
        errors=[{
            "field": "business_logic",
            "message": str(exc),
            "code": "business_error"
        }]
    )

    return JSONResponse(status_code=400, content=response)


def _internal_error(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected errors (500 Internal Server Error).
    """
    error_id = id(exc)
    logger.error(
        f"Internal server error [{error_id}]: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )

    response = error_response(
        message="Internal server error",
        errors=[{
            "field": "server",
            "message": "An unexpected error occurred. Please try again later.",
            "code": "internal_error"
        }]
    )

    return JSONResponse(status_code=500, content=response)


def register_exception_handler(app: FastAPI) -> None:
    """
    Register centralized exception handlers with FastAPI app.
    
    Uses @app.exception_handler decorators for:
    - RequestValidationError (422) - request body validation failures
    - HTTPException - all HTTP status codes
    - Exception - fallback for any unhandled exceptions (JWT, DB, business errors)
    """
    # Request validation errors (422) - JSON body validation failures
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _validation_error(request, exc)

    # HTTP exceptions
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _http_exception_handler(request, exc)

    # Generic exception fallback for any unhandled exceptions
    # This catches all other exceptions including:
    # - InvalidTokenError (JWT errors)
    # - SQLAlchemyError (database errors)
    # - ValueError (business logic errors)
    # - PermissionError (permission errors)
    # - Any other unhandled exceptions
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Handle specific exception types with appropriate responses
        if isinstance(exc, InvalidTokenError):
            return _authentication_error(request, "Invalid or expired token")
        elif isinstance(exc, SQLAlchemyError):
            return _database_error(request, exc)
        elif isinstance(exc, ValueError):
            return _business_error(request, exc)
        elif isinstance(exc, PermissionError):
            return _authorization_error(request, str(exc))
        elif "permission" in str(exc).lower():
            return _authorization_error(request, str(exc))

        # Generic fallback
        return _internal_error(request, exc)

    logger.info("Centralized exception handler registered")