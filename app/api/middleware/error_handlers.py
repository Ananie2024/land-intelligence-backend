"""
Error Handlers
Phase 1 — Section 2.5
Land Intelligence System
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
import traceback
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTPException with JSON error body.
        
        Args:
            request: FastAPI request object
            exc: HTTPException instance
            
        Returns:
            JSONResponse with error details
        """
        logger.warning(
            f"HTTP exception occurred",
            extra={
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "correlation_id": getattr(request.state, "correlation_id", ""),
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "http_exception"
                }
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """
        Handle Pydantic ValidationError with field details.
        
        Args:
            request: FastAPI request object
            exc: ValidationError instance
            
        Returns:
            JSONResponse with validation error details
        """
        # Extract validation errors
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error occurred",
            extra={
                "path": request.url.path,
                "errors": errors,
                "correlation_id": getattr(request.state, "correlation_id", ""),
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "message": "Validation error",
                    "type": "validation_error",
                    "details": errors
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle generic exceptions with sanitized message and full trace to log.
        
        Args:
            request: FastAPI request object
            exc: Exception instance
            
        Returns:
            JSONResponse with sanitized error message
        """
        # Log full traceback
        logger.error(
            f"Unhandled exception occurred",
            extra={
                "path": request.url.path,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc(),
                "correlation_id": getattr(request.state, "correlation_id", ""),
            },
            exc_info=True
        )
        
        # Return sanitized message to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Internal server error",
                    "type": "internal_error",
                    "correlation_id": getattr(request.state, "correlation_id", "")
                }
            }
        )# app/api/middleware/error_handlers.py
