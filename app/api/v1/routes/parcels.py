# app/api/v1/routes/parcels.py

"""
Parcel Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id, require_client_or_admin
from app.services.parcel.parcel_service import ParcelService
from app.schemas.parcel_schema import (
    ParcelCreate,
    ParcelUpdate,
    ParcelResponse,
    ParcelListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /parcels/  — paginated list with rich filtering
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ParcelListResponse,
    summary="List parcels",
    description="Return a paginated, filterable list of all active parcels.",
)
async def list_parcels(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    parish_id: Optional[str] = Query(None, description="Filter by parish UUID"),
    land_use_category_id: Optional[str] = Query(None, description="Filter by land use category UUID"),
    owner_name: Optional[str] = Query(None, description="Partial match on owner name"),
    parcel_number: Optional[str] = Query(None, description="Partial match on parcel number"),
    min_area_sqm: Optional[float] = Query(None, ge=0, description="Minimum area in m²"),
    max_area_sqm: Optional[float] = Query(None, ge=0, description="Maximum area in m²"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    
    filters = {}
    if owner_name:
        filters["owner_name"] = owner_name
    if parcel_number:
        filters["parcel_number"] = parcel_number
    if parish_id:
        filters["parish_id"] = parish_id
    if land_use_category_id:
        filters["land_use_category_id"] = land_use_category_id
    if min_area_sqm is not None:
        filters["min_area_sqm"] = min_area_sqm
    if max_area_sqm is not None:
        filters["max_area_sqm"] = max_area_sqm

    return await service.list_parcels(page=page, size=size, filters=filters)


# ---------------------------------------------------------------------------
# POST /parcels/  — create a new parcel
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ParcelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create parcel",
    description="Register a new land parcel. Parcel number must be unique. Parish must exist.",
)
async def create_parcel(
    payload: ParcelCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    _client_or_admin: str = Depends(require_client_or_admin),
):
    service = ParcelService(db)
    
    try:
        parcel = await service.create_parcel(payload, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/{parcel_id}  — fetch single parcel
# ---------------------------------------------------------------------------

@router.get(
    "/{parcel_id}",
    response_model=ParcelResponse,
    summary="Get parcel",
    description="Retrieve a single parcel by its UUID.",
)
async def get_parcel(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    parcel = await service.get_parcel(parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel '{parcel_id}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/by-number/{parcel_number}  — lookup by business key
# ---------------------------------------------------------------------------

@router.get(
    "/by-number/{parcel_number}",
    response_model=ParcelResponse,
    summary="Get parcel by number",
    description="Look up a parcel using its unique parcel number (e.g. 'P-2024-001').",
)
async def get_parcel_by_number(
    parcel_number: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    parcel = await service.get_parcel_by_number(parcel_number)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel number '{parcel_number}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/by-deed/{title_deed_number}  — lookup by title deed
# ---------------------------------------------------------------------------

@router.get(
    "/by-deed/{title_deed_number}",
    response_model=ParcelResponse,
    summary="Get parcel by title deed",
    description="Look up a parcel using its official title deed number.",
)
async def get_parcel_by_deed(
    title_deed_number: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    parcel = await service.get_parcel_by_deed(title_deed_number)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title deed '{title_deed_number}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/parish/{parish_id}  — all parcels in a parish
# ---------------------------------------------------------------------------

@router.get(
    "/parish/{parish_id}",
    response_model=ParcelListResponse,
    summary="List parcels by parish",
    description="Return all active parcels belonging to a specific parish.",
)
async def list_parcels_by_parish(
    parish_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    
    try:
        return await service.list_parcels_by_parish(parish_id=parish_id, page=page, size=size)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ---------------------------------------------------------------------------
# PATCH /parcels/{parcel_id}  — partial update
# ---------------------------------------------------------------------------

@router.patch(
    "/{parcel_id}",
    response_model=ParcelResponse,
    summary="Update parcel",
    description="Partially update a parcel. Uniqueness constraints on parcel_number and title_deed_number are enforced.",
)
async def update_parcel(
    parcel_id: str,
    payload: ParcelUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    
    try:
        parcel = await service.update_parcel(parcel_id, payload, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel '{parcel_id}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# DELETE /parcels/{parcel_id}  — soft delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{parcel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete parcel",
    description="Soft-delete a parcel. The parish parcel count is updated automatically.",
)
async def delete_parcel(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    service = ParcelService(db)
    deleted = await service.delete_parcel(parcel_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel '{parcel_id}' not found.",
        )
