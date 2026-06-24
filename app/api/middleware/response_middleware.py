# app/api/middleware/response_middleware.py
"""
Response Middleware for Standardized API Responses
Land Intelligence System
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class StandardizeResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware to standardize all API responses.
    Wraps successful responses with standard format.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and standardize response.
        """
        response = await call_next(request)
        
        # Only process JSON responses
        if not response.headers.get("content-type", "").startswith("application/json"):
            return response
        
        # Don't modify error responses (4xx, 5xx)
        if response.status_code >= 400:
            return response
        
        # Don't modify if already in standard format
        if response.status_code == 200:
            try:
                # Read response body safely across response types
                import json
                try:
                    body = await response.body()
                except AttributeError:
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    response = StarletteResponse(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )
                data = json.loads(body.decode("utf-8"))
                
                # Check if already standardized
                if isinstance(data, dict) and "success" in data and "timestamp" in data:
                    return JSONResponse(
                        content=data,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/json"
                    )
                
                # Wrap in standardized format
                from app.schemas.api_response import success_response
                standardized = success_response(
                    data=data,
                    message=None
                )
                
                return JSONResponse(
                    content=standardized,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json"
                )
            except Exception as e:
                logger.warning(f"Failed to standardize response: {str(e)}")
                return response
        
        return response


class PaginationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and wrap paginated responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and detect pagination patterns.
        """
        response = await call_next(request)
        
        if not response.headers.get("content-type", "").startswith("application/json"):
            return response
        
        if response.status_code >= 400:
            return response
        
        try:
            import json
            try:
                body = await response.body()
            except AttributeError:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                response = StarletteResponse(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            data = json.loads(body.decode("utf-8"))
            
            # Check if response has pagination structure
            if isinstance(data, dict) and all(k in data for k in ["items", "total", "page", "size"]):
                # This looks like a paginated response, wrap it
                from app.schemas.api_response import paginated_response
                standardized = paginated_response(
                    data=data.get("items", []),
                    page=data.get("page", 1),
                    size=data.get("size", 20),
                    total=data.get("total", 0),
                    message=None
                )
                # Remove original keys that are now in meta
                standardized_data = {k: v for k, v in data.items() if k not in ["items", "total", "page", "size", "pages"]}
                standardized["data"] = standardized_data
                
                return JSONResponse(
                    content=standardized,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json"
                )
        except Exception as e:
            logger.warning(f"Failed to process pagination: {str(e)}")
        
        return response