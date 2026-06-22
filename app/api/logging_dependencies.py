"""
Logging & Tracing Dependencies
Land Intelligence System
"""

import time
import uuid
import logging
from fastapi import Request
from typing import AsyncGenerator

from app.core.logging_config import set_correlation_id

logger = logging.getLogger(__name__)


async def correlation_id_logging(  # E501: line too long
    request: Request
) -> AsyncGenerator[str, None]:
    """
    Dependency that manages correlation ID and request logging.
    Replaces LoggingMiddleware by utilizing FastAPI's yield dependencies.
    This provides better compatibility with ContextVars and async tasks.
    """
    # 1. Start: Before request processing
    correlation_id = str(uuid.uuid4())

    # Set in context for structured logging
    set_correlation_id(correlation_id)
    request.state.correlation_id = correlation_id

    start_time = time.time()

    logger.info(
        "Request started",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else None,
        }
    )

    try:
        # Pass correlation_id to the route handler if it needs it
        yield correlation_id

    finally:
        # 2. End: After request processing (even if failed)
        duration = time.time() - start_time

        # Note: We can't access the response object here easily as a dependency
        # but we can log that the execution finished.
        logger.info(
            "Request finished",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration * 1000, 2),
            }
        )

        # Clear context
        set_correlation_id("")
