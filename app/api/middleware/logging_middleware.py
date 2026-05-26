# app/api/middleware/logging_middleware.py
"""
Logging Middleware
Phase 1 — Section 2.5
Land Intelligence System
"""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response
from typing import Callable

from app.core.logging_config import set_correlation_id

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs request details and adds correlation ID.
    
    Features:
    - Adds unique correlation_id to each request
    - Logs request method, path, response status, and duration
    - Makes correlation_id available to log formatters
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through logging middleware.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response from next handler
        """
        # Generate correlation ID for this request
        correlation_id = str(uuid.uuid4())
        
        # Store in thread-local for log formatters
        set_correlation_id(correlation_id)
        
        # Add correlation ID to request state for downstream use
        request.state.correlation_id = correlation_id
        
        # Record start time
        start_time = time.time()
        
        # Log request received
        logger.info(
            "Request received",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration even for exceptions
            duration = time.time() - start_time
            
            # Log exception
            logger.error(
                "Request failed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True
            )
            
            # Re-raise to let error handlers deal with it
            raise
        finally:
            # Clear correlation ID from thread-local
            set_correlation_id("")