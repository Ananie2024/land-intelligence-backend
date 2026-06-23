# app/schemas/api_response.py
"""
Standardized API Response Schemas
Land Intelligence System
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict, List, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class MetaData(BaseModel):
    """Metadata for paginated or filtered responses"""
    page: Optional[int] = None
    size: Optional[int] = None
    total: Optional[int] = None
    pages: Optional[int] = None


class ErrorDetail(BaseModel):
    """Error detail structure"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class APIResponse(BaseModel, Generic[T]):
    """
    Standardized API response format for all endpoints.
    
    Structure:
    {
        "success": bool,
        "data": T | None,
        "message": str | None,
        "errors": List[ErrorDetail] | None,
        "meta": MetaData | None,
        "timestamp": str
    }
    """
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None
    meta: Optional[MetaData] = None
    timestamp: str = None

    def __init__(self, **data: Any):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        super().__init__(**data)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {},
                "message": "Operation successful",
                "errors": None,
                "meta": None,
                "timestamp": "2024-01-01T00:00:00"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standardized paginated response format.
    """
    success: bool = True
    data: List[T] = []
    message: Optional[str] = None
    meta: MetaData
    timestamp: str = None

    def __init__(self, **data: Any):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        super().__init__(**data)


class ErrorResponse(BaseModel):
    """
    Standardized error response format.
    """
    success: bool = False
    data: None = None
    message: Optional[str] = None
    errors: List[ErrorDetail]
    timestamp: str = None

    def __init__(self, **data: Any):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        super().__init__(**data)


# Helper functions to create standardized responses

def success_response(
    data: Any = None,
    message: Optional[str] = "Operation successful",
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a success response dictionary.
    """
    response = {
        "success": True,
        "data": data,
        "message": message,
        "errors": None,
        "meta": meta,
        "timestamp": datetime.utcnow().isoformat()
    }
    return response


def error_response(
    message: str,
    errors: Optional[List[Dict[str, Any]]] = None,
    data: Any = None
) -> Dict[str, Any]:
    """
    Create an error response dictionary.
    """
    response = {
        "success": False,
        "data": data,
        "message": message,
        "errors": errors or [{"message": message}],
        "meta": None,
        "timestamp": datetime.utcnow().isoformat()
    }
    return response


def paginated_response(
    data: List[Any],
    page: int,
    size: int,
    total: int,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a paginated response dictionary.
    """
    pages = (total + size - 1) // size if size > 0 else 1
    
    return {
        "success": True,
        "data": data,
        "message": message or "Data retrieved successfully",
        "errors": None,
        "meta": {
            "page": page,
            "size": size,
            "total": total,
            "pages": pages
        },
        "timestamp": datetime.utcnow().isoformat()
    }