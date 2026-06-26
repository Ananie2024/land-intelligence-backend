# app/api/v1/routes/qr_codes.py
"""
QR Code Registry API Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.services.qr.qr_service import QRCodeService
from app.schemas.qr_code_schema import (
    QRCodeResponse,
    QRCodeGenerateRequest,
    QRCodeVerifyRequest,
    QRCodeVerifyResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate/parcel/{parcel_id}", response_model=QRCodeResponse)
async def generate_parcel_qr(
    parcel_id: str,
    expires_days: Optional[int] = Query(None, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Generate a Digital Testimony QR code for a parcel."""
    from app.repositories.qr_registry_repository import QRRegistryRepository
    from app.repositories.parcel_repository import ParcelRepository
    from app.repositories.document_repository import DocumentRepository
    
    service = QRCodeService(
        db=db,
        qr_repo=QRRegistryRepository(db),
        parcel_repo=ParcelRepository(db),
        document_repo=DocumentRepository(db),
    )
    
    try:
        qr_entry = await service.generate_parcel_qr(parcel_id, expires_days, user_id)
        return qr_entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/generate/document/{document_id}", response_model=QRCodeResponse)
async def generate_document_qr(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Generate an integrity QR code for a specific document."""
    from app.repositories.qr_registry_repository import QRRegistryRepository
    from app.repositories.parcel_repository import ParcelRepository
    from app.repositories.document_repository import DocumentRepository
    
    service = QRCodeService(
        db=db,
        qr_repo=QRRegistryRepository(db),
        parcel_repo=ParcelRepository(db),
        document_repo=DocumentRepository(db),
    )
    
    try:
        qr_entry = await service.generate_document_qr(document_id, user_id)
        return qr_entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/verify", response_model=QRCodeVerifyResponse)
async def verify_qr_code(
    request: QRCodeVerifyRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Verify a QR code and check its integrity."""
    from app.repositories.qr_registry_repository import QRRegistryRepository
    from app.repositories.parcel_repository import ParcelRepository
    from app.repositories.document_repository import DocumentRepository
    
    service = QRCodeService(
        db=db,
        qr_repo=QRRegistryRepository(db),
        parcel_repo=ParcelRepository(db),
        document_repo=DocumentRepository(db),
    )
    
    return await service.verify_qr_code(request.code)


@router.get("/{qr_id}", response_model=QRCodeResponse)
async def get_qr_details(
    qr_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get QR code registry details."""
    from app.repositories.qr_registry_repository import QRRegistryRepository
    
    service = QRCodeService(
        db=db,
        qr_repo=QRRegistryRepository(db),
        parcel_repo=None,
        document_repo=None,
    )
    
    qr_entry = await service.get_qr_details(qr_id)
    if not qr_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR Code {qr_id} not found"
        )
    return qr_entry


@router.delete("/{qr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_qr_code(
    qr_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Revoke a QR code."""
    from app.repositories.qr_registry_repository import QRRegistryRepository
    
    service = QRCodeService(
        db=db,
        qr_repo=QRRegistryRepository(db),
        parcel_repo=None,
        document_repo=None,
    )
    
    success = await service.revoke_qr_code(qr_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR Code {qr_id} not found"
        )
    return None