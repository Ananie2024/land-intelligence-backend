# app/api/middleware/response_middleware.py
"""
Response Middleware
Land Intelligence System

Standardizes successful JSON responses from API routes and detects
paginated payloads.

Key constraint
--------------
The OpenAPI schema endpoint (/api/openapi.json) and Swagger/ReDoc UI
endpoints (/api/docs, /api/redoc) must NEVER be wrapped.
"""

import json
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.api_response import success_response, paginated_response

logger = logging.getLogger(__name__)

PASSTHROUGH_PREFIXES = (
    "/api/openapi.json",
    "/api/docs",
    "/api/redoc",
    "/health",
    "/",
)


def _is_passthrough(path: str) -> bool:
    return any(path == p or path.startswith(p) for p in PASSTHROUGH_PREFIXES)


async def _read_body(response: Response) -> bytes:
    try:
        return response.body
    except (RuntimeError, AttributeError):
        pass
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
    return body


class StandardizeResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if _is_passthrough(request.url.path):
            return response

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response
        if response.status_code >= 400:
            return response

        try:
            body = await _read_body(response)
            data = json.loads(body.decode("utf-8"))

            if isinstance(data, dict) and "success" in data and "timestamp" in data:
                return JSONResponse(content=data, status_code=response.status_code)

            standardized = success_response(data=data)
            return JSONResponse(content=standardized, status_code=response.status_code)

        except Exception as exc:
            logger.warning("StandardizeResponseMiddleware: failed to wrap response: %s", exc)
            return response


class PaginationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if _is_passthrough(request.url.path):
            return response

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response
        if response.status_code >= 400:
            return response

        try:
            body = await _read_body(response)
            data = json.loads(body.decode("utf-8"))

            if isinstance(data, dict) and "success" in data and "timestamp" in data:
                return JSONResponse(content=data, status_code=response.status_code)

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