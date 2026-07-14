"""
QR Code Verification Service
Phase 3 — Section 4.1
Land Intelligence System
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from app.repositories.qr_registry_repository import QRRegistryRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.parcel_repository import ParcelRepository
from app.schemas.qr_code_schema import QRCodeVerifyResponse

logger = logging.getLogger(__name__)


class VerificationService:
    """
    Handles verification of scanned QR codes.
    
    Validates QR codes against the registry, checks for expiration/revocation,
    and performs deep integrity checks by comparing encoded hashes 
    against current database/file state.
    """
    
    def __init__(
        self,
        qr_repo: QRRegistryRepository,
        document_repo: DocumentRepository,
        parcel_repo: ParcelRepository
    ):
        """
        Initialize verification service.
        
        Args:
            qr_repo: QR registry repository
            document_repo: Document repository
            parcel_repo: Parcel repository
        """
        self.qr_repo = qr_repo
        self.document_repo = document_repo
        self.parcel_repo = parcel_repo
        
    async def verify_code(self, qr_string: str) -> QRCodeVerifyResponse:
        """
        Perform a full verification of a QR code.
        
        Args:
            qr_string: Unique QR code string
            
        Returns:
            Verification response with validity and details
        """
        # 1. Basic Registry Check
        qr_entry = await self.qr_repo.get_by_code(qr_string)
        
        if not qr_entry:
            return QRCodeVerifyResponse(
                is_valid=False,
                code=qr_string,
                code_type="UNKNOWN",
                is_revoked=False,
                message="QR code not found in registry"
            )
            
        # Signature Check
        payload = qr_entry.data_payload
        if not payload or "sig" not in payload:
            return QRCodeVerifyResponse(
                is_valid=False,
                code=qr_string,
                code_type=qr_entry.code_type or "UNKNOWN",
                is_revoked=bool(qr_entry.is_revoked),
                message="Invalid or missing signature in payload"
            )

        import hmac
        import hashlib
        import json
        from app.core.config import settings

        payload_copy = dict(payload)
        sig = payload_copy.pop("sig")
        serialized = json.dumps(payload_copy, sort_keys=True)
        key = settings.SECRET_KEY.encode('utf-8')
        expected_sig = hmac.new(key, serialized.encode('utf-8'), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected_sig):
            return QRCodeVerifyResponse(
                is_valid=False,
                code=qr_string,
                code_type=qr_entry.code_type or "UNKNOWN",
                is_revoked=bool(qr_entry.is_revoked),
                message="Signature verification failed"
            )
            
        # 2. Status Checks (Revoked/Expired/Active)
        if not qr_entry.is_active:
            return QRCodeVerifyResponse(
                is_valid=False,
                code=qr_string,
                code_type=qr_entry.code_type,
                is_revoked=False,
                message="QR code is no longer active"
            )
            
        if qr_entry.is_revoked:
            return QRCodeVerifyResponse(
                is_valid=False,
                code=qr_string,
                code_type=qr_entry.code_type,
                is_revoked=True,
                message="QR code has been revoked"
            )
            
        if qr_entry.expires_at and qr_entry.expires_at < datetime.now(timezone.utc):
            return QRCodeVerifyResponse(
                is_valid=False,
                code=qr_string,
                code_type=qr_entry.code_type,
                is_revoked=False,
                expires_at=qr_entry.expires_at,
                message="QR code has expired"
            )
            
        # 3. Deep Integrity Check (Compare payload with current DB state)
        integrity_valid, integrity_msg = await self._check_integrity(qr_entry)
        
        # 4. Record Access
        await self.qr_repo.record_access(qr_string)
        
        # Look up parcel UPI if parcel_id exists
        parcel_upi = None
        if qr_entry.parcel_id:
            parcel = await self.parcel_repo.get(qr_entry.parcel_id)
            if parcel:
                parcel_upi = parcel.upi
        
        return QRCodeVerifyResponse(
            is_valid=integrity_valid,
            code=qr_string,
            code_type=qr_entry.code_type,
            parcel_upi=parcel_upi,
            document_id=str(qr_entry.document_id) if qr_entry.document_id else None,
            expires_at=qr_entry.expires_at,
            is_revoked=qr_entry.is_revoked,
            data_payload=qr_entry.data_payload,
            message=integrity_msg
        )

    async def _check_integrity(self, qr_entry: Any) -> Tuple[bool, str]:
        """
        Check if the data in the QR still matches the database.
        """
        payload = qr_entry.data_payload
        if not payload or "data" not in payload:
            return False, "Malformed QR payload"
            
        data = payload["data"]
        
        if qr_entry.code_type == "PARCEL":
            parcel = await self.parcel_repo.get(qr_entry.parcel_id)
            if not parcel:
                return False, "Target parcel no longer exists"
            
            # Verify owner hasn't changed (basic check)
            if data.get("owner") != parcel.owner_name:
                return False, "Ownership information has changed since QR generation"
                
            return True, "QR code is valid and integrity verified"
            
        elif qr_entry.code_type == "DOCUMENT":
            document = await self.document_repo.get(qr_entry.document_id)
            if not document:
                return False, "Target document no longer exists"
            
            # Verify file checksum hasn't changed
            if data.get("hash") != document.checksum:
                return False, "Document file has been modified or replaced (Integrity Failure)"
                
            return True, "QR code is valid and document integrity verified"
            
        return True, "QR code is valid (Basic verification only)"
