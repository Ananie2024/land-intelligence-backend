# app/api/v1/routes/physical_locations.py
"""
Physical Locations & Cabinets API Routes
Phase 2 — Section 3.2
Land Intelligence System
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.services.location.location_service import LocationService
from app.schemas.physical_location_schema import (
    PhysicalLocationFinderRequest,
    PhysicalLocationFinderResponse,
    PhysicalLocationCreate,
    PhysicalLocationUpdate,
    StorageCabinetCreate,
    StorageCabinetUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create physical location",
    description="Register a new physical archive room, warehouse, or shelf location."
)
async def create_location(
    payload: PhysicalLocationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        location = await service.create_location(payload, user_id)
        return location
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating location: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register physical location."
        )


@router.get(
    "",
    response_model=List[Dict[str, Any]],
    summary="List physical locations",
    description="List active physical archive locations.",
    include_in_schema=False,
)
async def list_locations_no_slash(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        return await service.list_locations(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error listing locations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve physical locations."
        )


@router.get(
    "/",
    response_model=List[Dict[str, Any]],
    summary="List physical locations",
    description="List active physical archive locations."
)
async def list_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    return await list_locations_no_slash(skip=skip, limit=limit, db=db, _=None)


@router.get(
    "/{location_id}",
    response_model=Dict[str, Any],
    summary="Get physical location",
    description="Fetch details of a single physical location by UUID."
)
async def get_location(
    location_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        location = await service.get_location(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID '{location_id}' not found."
            )
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve physical location."
        )


@router.patch(
    "/{location_id}",
    response_model=Dict[str, Any],
    summary="Update physical location",
    description="Partially update physical location parameters."
)
async def update_location(
    location_id: str,
    payload: PhysicalLocationUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        location = await service.update_location(location_id, payload, user_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID '{location_id}' not found."
            )
        return location
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update physical location."
        )


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete physical location",
    description="Soft-delete a physical location. Cascading constraints apply."
)
async def delete_location(
    location_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        deleted = await service.delete_location(location_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID '{location_id}' not found."
            )
        from app.schemas.api_response import success_response
        return success_response(message=f"Location '{location_id}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete location."
        )


@router.post(
    "/find",
    response_model=PhysicalLocationFinderResponse,
    summary="Locate archive document",
    description="Resolve and locate the physical storage coordinates of a document or parcel."
)
async def locate_document(
    payload: PhysicalLocationFinderRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        res = await service.locate_document(payload.model_dump())
        return res
    except Exception as e:
        logger.error(f"Error finding physical document location: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal search resolution failed."
        )


@router.post(
    "/cabinets",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create cabinet",
    description="Create a storage cabinet under an existing physical location."
)
async def create_cabinet(
    payload: StorageCabinetCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        cabinet = await service.create_cabinet(payload, user_id)
        return cabinet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating storage cabinet: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register storage cabinet."
        )


@router.get(
    "/cabinets/{cabinet_id}",
    response_model=Dict[str, Any],
    summary="Get cabinet detail",
    description="Retrieve details of a storage cabinet by UUID."
)
async def get_cabinet(
    cabinet_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        cabinet = await service.get_cabinet(cabinet_id)
        if not cabinet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Storage cabinet '{cabinet_id}' not found."
            )
        return cabinet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting storage cabinet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage cabinet."
        )


@router.patch(
    "/cabinets/{cabinet_id}",
    response_model=Dict[str, Any],
    summary="Update cabinet details",
    description="Partially update a cabinet (capacity, location reference, count, coordinates)."
)
async def update_cabinet(
    cabinet_id: str,
    payload: StorageCabinetUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        cabinet = await service.update_cabinet(cabinet_id, payload, user_id)
        if not cabinet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cabinet '{cabinet_id}' not found."
            )
        return cabinet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating storage cabinet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cabinet."
        )


@router.get(
    "/{location_id}/grid",
    response_model=Dict[str, Any],
    summary="Get grid room map layout",
    description="Retrieve the visual row-column map coordinate grid representation of all cabinets in this location."
)
async def get_location_grid(
    location_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        service = LocationService(db)
        return await service.get_location_grid(location_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error mapping cabinet grid for location {location_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to build room grid map."
        )