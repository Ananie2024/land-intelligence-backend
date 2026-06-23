# app/services/qr/qr_service.py
"""
QR Code Registry Service
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.qr_code_schema import QRCodeCreate, QRCodeResponse
from app.repositories.qr_registry_repository import QRRegistryRepository
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.document_repository import DocumentRepository
from app.services.qr.qr_generator import QRGenerator
from app.services.qr.digital_testimony_builder import DigitalTestimonyBuilder
from app.services.qr.verification_service import VerificationService
from app.models.qr_code_registry import QRCodeRegistry

logger = logging.getLogger(__name__)


class QRCodeService:
    """
    Business logic layer for QR code operations.
    """

    def __init__(
        self,
        db: AsyncSession,
        qr_repo: QRRegistryRepository,
        parcel_repo: ParcelRepository,
        document_repo: DocumentRepository,
    ):
        self.db = db
        self.qr_repo = qr_repo
        self.parcel_repo = parcel_repo
        self.document_repo = document_repo
        self.qr_generator = QRGenerator()
        self.testimony_builder = DigitalTestimonyBuilder(document_repo)

    async def generate_parcel_qr(
        self,
        parcel_id: str,
        expires_days: Optional[int],
        user_id: str
    ) -> QRCodeRegistry:
        """
        Generate a Digital Testimony QR code for a parcel.
        """
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            raise ValueError(f"Parcel {parcel_id} not found")

        payload = await self.testimony_builder.build_parcel_payload(parcel)
        qr_string, file_path = self.qr_generator.generate(payload, prefix="PRC")

        expires_at = datetime.utcnow() + timedelta(days=expires_days) if expires_days else None

        qr_entry_data = QRCodeCreate(
            parcel_id=parcel_id,
            code_type="PARCEL",
            data_payload=payload,
            expires_at=expires_at,
            metadata={"generated_by": user_id}
        )

        instance_data = qr_entry_data.model_dump(exclude_none=True)
        instance_data["code"] = qr_string
        instance_data["file_path"] = file_path

        qr_entry = QRCodeRegistry(**instance_data)
        self.db.add(qr_entry)
        await self.db.flush()
        await self.db.refresh(qr_entry)

        return qr_entry

    async def generate_document_qr(
        self,
        document_id: str,
        user_id: str
    ) -> QRCodeRegistry:
        """
        Generate an integrity QR code for a specific document.
        """
        document = await self.document_repo.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        payload = await self.testimony_builder.build_document_payload(document)
        qr_string, file_path = self.qr_generator.generate(payload, prefix="DOC")

        qr_entry_data = QRCodeCreate(
            document_id=document_id,
            parcel_id=str(document.parcel_id) if document.parcel_id else None,
            code_type="DOCUMENT",
            data_payload=payload,
            metadata={"generated_by": user_id}
        )

        instance_data = qr_entry_data.model_dump(exclude_none=True)
        instance_data["code"] = qr_string
        instance_data["file_path"] = file_path

        qr_entry = QRCodeRegistry(**instance_data)
        self.db.add(qr_entry)
        await self.db.flush()
        await self.db.refresh(qr_entry)

        return qr_entry

    async def verify_qr_code(self, code: str) -> Dict[str, Any]:
        """
        Verify a QR code and check its integrity.
        """
        verifier = VerificationService(
            self.qr_repo,
            self.document_repo,
            self.parcel_repo
        )
        return await verifier.verify_code(code)

    async def get_qr_details(self, qr_id: str) -> Optional[QRCodeRegistry]:
        """
        Get QR code registry details.
        """
        return await self.qr_repo.get(qr_id)

    async def revoke_qr_code(self, qr_id: str) -> bool:
        """
        Revoke a QR code.
        """
        success = await self.qr_repo.soft_delete(qr_id)
        if not success:
            return False
        await self.db.commit()
        return True