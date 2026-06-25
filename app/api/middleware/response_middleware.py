# app/api/middleware/response_middleware.py
"""
Response Middleware
Land Intelligence System

Standardizes successful JSON responses and detects paginated payloads.

Root cause of the previous Content-Length crash
------------------------------------------------
Both middleware classes were reading the response body, wrapping it in a
larger envelope, then constructing a new JSONResponse while copying the
*original* headers — including the original (now stale) Content-Length.
uvicorn validates Content-Length on the way out and raises:
    RuntimeError: Response content longer than Content-Length

Fix: never forward headers when building a replacement JSONResponse.
JSONResponse sets its own correct Content-Length automatically.
"""

import json
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.api_response import success_response, paginated_response

logger = logging.getLogger(__name__)


async def _read_body(response: Response) -> bytes:
    """
    Read the full response body regardless of response type.
    BaseHTTPMiddleware responses expose body via .body() on StreamingResponse
    variants, or via direct iteration.
    """
    if hasattr(response, "body"):
        return await response.body()

    body = b""
    async for chunk in response.body_iterator:  # type: ignore[attr-defined]
        body += chunk
    return body


class StandardizeResponseMiddleware(BaseHTTPMiddleware):
    """
    Wraps successful (2xx) JSON responses in the project's standard envelope:

        {
            "success": true,
            "data": <original payload>,
            "message": "Operation successful",
            "errors": null,
            "meta": null,
            "timestamp": "..."
        }

    Passes through unchanged:
    - Non-JSON responses (HTML, files, streaming)
    - 4xx / 5xx responses (handled by the error handler)
    - Responses already in standard format (contain both "success" and "timestamp")
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Only touch successful JSON responses
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response
        if response.status_code >= 400:
            return response

        try:
            body = await _read_body(response)
            data = json.loads(body.decode("utf-8"))

            # Already standardized — return as-is (no header copy)
            if isinstance(data, dict) and "success" in data and "timestamp" in data:
                return JSONResponse(content=data, status_code=response.status_code)

            # Wrap in standard envelope
            standardized = success_response(data=data)
            return JSONResponse(content=standardized, status_code=response.status_code)

        except Exception as exc:
            logger.warning("StandardizeResponseMiddleware: failed to wrap response: %s", exc)
            return response


class PaginationMiddleware(BaseHTTPMiddleware):
    """
    Detects paginated payloads — dicts that contain all of
    { items, total, page, size } — and re-wraps them using the
    project's paginated_response envelope.

    Must run *before* StandardizeResponseMiddleware in the middleware stack
    (i.e. added to the app after it, because FastAPI stacks middleware in
    reverse addition order).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response
        if response.status_code >= 400:
            return response

        try:
            body = await _read_body(response)
            data = json.loads(body.decode("utf-8"))

            # Already fully standardized — leave it alone
            if isinstance(data, dict) and "success" in data and "timestamp" in data:
                return JSONResponse(content=data, status_code=response.status_code)

            # Paginated payload detection
            if isinstance(data, dict) and all(
                k in data for k in ("items", "total", "page", "size")
            ):
                standardized = paginated_response(
                    data=data["items"],
                    page=data["page"],
                    size=data["size"],
                    total=data["total"],
                )
                return JSONResponse(
                    content=standardized, status_code=response.status_code
                )

        except Exception as exc:
            logger.warning("PaginationMiddleware: failed to process response: %s", exc)

        return response