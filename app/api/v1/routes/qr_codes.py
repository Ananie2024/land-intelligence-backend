# app/api/v1/routes/qr_codes.py

"""
QR Code Registry API Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.schemas.qr_code_schema import (
    QRCodeResponse,
    QRCodeGenerateRequest,
    QRCodeVerifyRequest,
    QRCodeVerifyResponse,
    QRCodeCreate
)
from app.services.qr.qr_generator import QRGenerator
from app.services.qr.digital_testimony_builder import DigitalTestimonyBuilder
from app.services.qr.verification_service import VerificationService
from app.repositories.qr_registry_repository import QRRegistryRepository
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency factories
async def get_qr_generator() -> QRGenerator:
    return QRGenerator()

async def get_testimony_builder(db: AsyncSession = Depends(get_db)) -> DigitalTestimonyBuilder:
    return DigitalTestimonyBuilder(DocumentRepository(db))

async def get_verification_service(db: AsyncSession = Depends(get_db)) -> VerificationService:
    return VerificationService(
        QRRegistryRepository(db),
        DocumentRepository(db),
        ParcelRepository(db)
    )


@router.post("/generate/parcel/{parcel_id}", response_model=QRCodeResponse)
async def generate_parcel_qr(
    parcel_id: str,
    expires_days: Optional[int] = Query(None, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    qr_gen: QRGenerator = Depends(get_qr_generator),
    builder: DigitalTestimonyBuilder = Depends(get_testimony_builder)
):
    """Generate a Digital Testimony QR code for a parcel."""
    parcel_repo = ParcelRepository(db)
    parcel = await parcel_repo.get(parcel_id)
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel {parcel_id} not found"
        )
        
    # 1. Build Payload
    payload = await builder.build_parcel_payload(parcel)
    
    # 2. Generate QR Image
    qr_string, file_path = qr_gen.generate(payload, prefix="PRC")
    
    # 3. Save to Registry
    expires_at = datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
    
    qr_entry_data = QRCodeCreate(
        parcel_id=parcel_id,
        code_type="PARCEL",
        data_payload=payload,
        expires_at=expires_at,
        metadata={"generated_by": user_id}
    )
    
    qr_repo = QRRegistryRepository(db)
    # We need to manually add the generated system fields
    instance_data = qr_entry_data.model_dump(exclude_none=True)
    instance_data["code"] = qr_string
    instance_data["file_path"] = file_path
    
    from app.models.qr_code_registry import QRCodeRegistry
    qr_entry = QRCodeRegistry(**instance_data)
    db.add(qr_entry)
    await db.flush()
    await db.refresh(qr_entry)
    
    return qr_entry


@router.post("/generate/document/{document_id}", response_model=QRCodeResponse)
async def generate_document_qr(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    qr_gen: QRGenerator = Depends(get_qr_generator),
    builder: DigitalTestimonyBuilder = Depends(get_testimony_builder)
):
    """Generate an integrity QR code for a specific document."""
    doc_repo = DocumentRepository(db)
    document = await doc_repo.get(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
        
    # 1. Build Payload
    payload = await builder.build_document_payload(document)
    
    # 2. Generate QR Image
    qr_string, file_path = qr_gen.generate(payload, prefix="DOC")
    
    # 3. Save to Registry
    qr_entry_data = QRCodeCreate(
        document_id=document_id,
        parcel_id=str(document.parcel_id) if document.parcel_id else None,
        code_type="DOCUMENT",
        data_payload=payload,
        metadata={"generated_by": user_id}
    )
    
    qr_repo = QRRegistryRepository(db)
    instance_data = qr_entry_data.model_dump(exclude_none=True)
    instance_data["code"] = qr_string
    instance_data["file_path"] = file_path
    
    from app.models.qr_code_registry import QRCodeRegistry
    qr_entry = QRCodeRegistry(**instance_data)
    db.add(qr_entry)
    await db.flush()
    await db.refresh(qr_entry)
    
    return qr_entry


@router.post("/verify", response_model=QRCodeVerifyResponse)
async def verify_qr_code(
    request: QRCodeVerifyRequest,
    verifier: VerificationService = Depends(get_verification_service)
):
    """Verify a QR code and check its integrity."""
    return await verifier.verify_code(request.code)


@router.get("/{qr_id}", response_model=QRCodeResponse)
async def get_qr_details(
    qr_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get QR code registry details."""
    qr_repo = QRRegistryRepository(db)
    qr_entry = await qr_repo.get(qr_id)
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
    qr_repo = QRRegistryRepository(db)
    success = await qr_repo.soft_delete(qr_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QR Code {qr_id} not found"
        )
    return None
