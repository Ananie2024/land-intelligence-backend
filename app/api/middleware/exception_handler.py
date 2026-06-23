# app/api/middleware/exception_handler.py
"""
Centralized Global Exception Handler
Land Intelligence System
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from jose import JWTError
import logging
from typing import Dict, Any, Optional

from app.schemas.api_response import error_response, ErrorDetail

logger = logging.getLogger(__name__)


class CentralizedExceptionMiddleware(BaseHTTPMiddleware):
    """
    Centralized exception handling middleware.
    Catches and standardizes all exceptions across the application.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            return await self._handle_exception(request, exc)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle and categorize exceptions.
        """
        # Import here to avoid circular dependencies
        from app.models.user import UserRole
        
        # Determine exception type and map to appropriate response
        exc_type = type(exc).__name__
        
        # 1. Validation Errors (Pydantic)
        if isinstance(exc, ValidationError):
            logger.warning(f"Validation error: {str(exc)}")
            return self._validation_error(exc)
        
        # 2. JWT Errors
        if isinstance(exc, JWTError):
            logger.warning(f"JWT error: {str(exc)}")
            return self._authentication_error("Invalid or expired token")
        
        # 3. HTTP Exceptions (already handled by FastAPI)
        if isinstance(exc, StarletteHTTPException):
            logger.warning(f"HTTP exception: {exc.detail}")
            return self._http_exception(exc)
        
        # 4. Database Errors
        if isinstance(exc, SQLAlchemyError):
            logger.error(f"Database error: {str(exc)}", exc_info=True)
            return self._database_error(exc)
        
        # 5. Business Logic Errors (ValueError, custom exceptions)
        if isinstance(exc, ValueError):
            logger.warning(f"Business logic error: {str(exc)}")
            return self._business_error(exc)
        
        # 6. Permission/Authentication Errors
        if isinstance(exc, PermissionError) or "permission" in str(exc).lower():
            logger.warning(f"Permission error: {str(exc)}")
            return self._authorization_error(str(exc))
        
        # 7. Generic unexpected errors
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return self._internal_error(exc, request)
    
    def _validation_error(self, exc: ValidationError) -> JSONResponse:
        """
        Handle Pydantic validation errors (400 Bad Request).
        """
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            errors.append(ErrorDetail(
                field=field,
                message=error.get("msg", "Validation failed"),
                code=error.get("type", "validation_error")
            ))
        
        response = error_response(
            message="Validation error",
            errors=[e.model_dump() for e in errors]
        )
        
        return JSONResponse(
            status_code=400,
            content=response
        )
    
    def _authentication_error(self, message: str) -> JSONResponse:
        """
        Handle authentication errors (401 Unauthorized).
        """
        response = error_response(
            message=message or "Authentication required",
            errors=[ErrorDetail(
                field="token",
                message=message,
                code="authentication_error"
            ).model_dump()]
        )
        
        return JSONResponse(
            status_code=401,
            content=response,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _authorization_error(self, message: str) -> JSONResponse:
        """
        Handle authorization errors (403 Forbidden).
        """
        response = error_response(
            message=message or "Insufficient permissions",
            errors=[ErrorDetail(
                field="permissions",
                message=message,
                code="authorization_error"
            ).model_dump()]
        )
        
        return JSONResponse(
            status_code=403,
            content=response
        )
    
    def _http_exception(self, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle FastAPI HTTP exceptions.
        """
        status_code = exc.status_code
        detail = exc.detail
        
        # Categorize based on status code
        if status_code == 401:
            return self._authentication_error(detail)
        elif status_code == 403:
            return self._authorization_error(detail)
        elif status_code == 404:
            response = error_response(
                message=detail or "Resource not found",
                errors=[ErrorDetail(
                    field="resource",
                    message=detail,
                    code="not_found"
                ).model_dump()]
            )
            return JSONResponse(status_code=404, content=response)
        elif status_code == 409:
            response = error_response(
                message=detail or "Conflict",
                errors=[ErrorDetail(
                    field="conflict",
                    message=detail,
                    code="conflict"
                ).model_dump()]
            )
            return JSONResponse(status_code=409, content=response)
        elif status_code == 422:
            return self._validation_error_from_dict(detail)
        else:
            response = error_response(
                message=detail or "HTTP error occurred",
                errors=[ErrorDetail(
                    message=str(detail),
                    code=f"http_{status_code}"
                ).model_dump()]
            )
            return JSONResponse(status_code=status_code, content=response)
    
    def _validation_error_from_dict(self, detail: Dict) -> JSONResponse:
        """
        Convert FastAPI validation error dict to standardized error.
        """
        errors = []
        for error in detail.get("errors", [detail]):
            errors.append(ErrorDetail(
                field=error.get("loc", ["unknown"])[-1] if isinstance(error.get("loc"), list) else None,
                message=error.get("msg", "Validation failed"),
                code=error.get("type", "validation_error")
            ).model_dump())
        
        response = error_response(
            message="Validation error",
            errors=errors
        )
        
        return JSONResponse(status_code=422, content=response)
    
    def _business_error(self, exc: ValueError) -> JSONResponse:
        """
        Handle business logic errors (400 Bad Request).
        """
        response = error_response(
            message=str(exc) or "Business logic error",
            errors=[ErrorDetail(
                field="business_logic",
                message=str(exc),
                code="business_error"
            ).model_dump()]
        )
        
        return JSONResponse(status_code=400, content=response)
    
    def _database_error(self, exc: SQLAlchemyError) -> JSONResponse:
        """
        Handle database errors (500 Internal Server Error).
        """
        response = error_response(
            message="Database operation failed",
            errors=[ErrorDetail(
                field="database",
                message="An internal database error occurred",
                code="database_error"
            ).model_dump()]
        )
        
        return JSONResponse(status_code=500, content=response)
    
    def _internal_error(self, exc: Exception, request: Request) -> JSONResponse:
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
            errors=[ErrorDetail(
                field="server",
                message="An unexpected error occurred. Please try again later.",
                code="internal_error"
            ).model_dump()]
        )
        
        return JSONResponse(status_code=500, content=response)


def register_exception_handler(app: FastAPI) -> None:
    """
    Register centralized exception handler with FastAPI app.
    """
    # Add centralized middleware
    app.add_middleware(CentralizedExceptionMiddleware)
    
    logger.info("Centralized exception handler registered")