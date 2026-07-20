# app/api/v1/routes/parishes.py
"""
Parish Routes
Phase 3 — Section 4.1
Land Intelligence System
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id, require_admin, require_parish_access, get_current_user_from_db
from app.services.parish.parish_service import ParishService
from app.schemas.parish_schema import (
    ParishCreate,
    ParishUpdate,
    ParishResponse,
    ParishListResponse,
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /parishes/  - paginated list with optional name search
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=ParishListResponse,
    summary="List parishes",
    description="Return a paginated list of all active parishes, with optional name search.",
    include_in_schema=False,
)
async def list_parishes_no_slash(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Search by parish name (partial match)"),
    db: AsyncSession = Depends(get_db),
    _: Optional[str] = Depends(get_current_user_id),
):
    service = ParishService(db)
    
    return await service.list_parishes(page=page, size=size, name=name)


@router.get(
    "/",
    response_model=ParishListResponse,
    summary="List parishes",
    description="Return a paginated list of all active parishes, with optional name search.",
)
async def list_parishes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Search by parish name (partial match)"),
    db: AsyncSession = Depends(get_db),
    _user_id: str = Depends(get_current_user_id),
):
     return await list_parishes_no_slash(page=page, size=size, name=name, db=db, _=None)


# ---------------------------------------------------------------------------
# GET /parishes/all  - list all parishes without pagination (for dropdowns)
# ---------------------------------------------------------------------------

@router.get(
    "/all",
    response_model=list[ParishResponse],
    summary="List all parishes",
    description="Return all active parishes without pagination. Used for dropdown/select inputs.",
)
async def list_all_parishes(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParishService(db)
    return await service.list_all_parishes()


# ---------------------------------------------------------------------------
# POST /parishes  - create a new parish (no trailing slash)
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=ParishResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create parish",
    description="Create a new parish.",
    include_in_schema=False,
)
async def create_parish_no_slash(
    payload: ParishCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
):
    service = ParishService(db)
    return await service.create_parish(payload, user_id)


# ---------------------------------------------------------------------------
# POST /parishes/  - create a new parish (with trailing slash)
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ParishResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create parish",
    description="Create a new parish.",
)
async def create_parish(
    payload: ParishCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    _admin: str = Depends(require_admin),
):
    service = ParishService(db)
    return await service.create_parish(payload, user_id)


# ---------------------------------------------------------------------------
# GET /parishes/{parish_id}  - fetch single parish
# ---------------------------------------------------------------------------

@router.get(
    "/{parish_id}",
    response_model=ParishResponse,
    summary="Get parish",
    description="Retrieve a single parish by its UUID.",
)
async def get_parish(
    parish_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParishService(db)
    parish = await service.get_parish(parish_id)

    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    return parish


# ---------------------------------------------------------------------------
# PATCH /parishes/{parish_id}  - partial update
# ---------------------------------------------------------------------------

@router.patch(
    "/{parish_id}",
    response_model=ParishResponse,
    summary="Update parish",
    description="Partially update a parish. Only provided fields are changed.",
)
async def update_parish(
    parish_id: str,
    payload: ParishUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    user: User = Depends(get_current_user_from_db),
):
    await require_parish_access(parish_id, user)
    
    service = ParishService(db)
    
    parish = await service.update_parish(parish_id, payload, user_id)

    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    return parish


# ---------------------------------------------------------------------------
# DELETE /parishes/{parish_id}  - soft delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{parish_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete parish",
    description="Soft-delete a parish (sets is_active=False). Parcels are not removed.",
)
async def delete_parish(
    parish_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    user: User = Depends(get_current_user_from_db),
    _admin: str = Depends(require_admin),
):
    await require_parish_access(parish_id, user)
    
    service = ParishService(db)
    deleted = await service.delete_parish(parish_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )
    
    from app.schemas.api_response import success_response
    return success_response(message=f"Parish '{parish_id}' deleted successfully")