"""
Digital Testimony Builder Service
Phase 3 — Section 4.1
Land Intelligence System
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.parcel import Parcel
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class DigitalTestimonyBuilder:
    """
    Constructs a verifiable data payload for QR codes.
    
    Combines parcel details, ownership info, and document checksums 
    into a secure JSON structure that represents the "digital testimony" 
    of a land parcel's status.
    """
    
    def __init__(self, document_repo: DocumentRepository):
        """
        Initialize builder with dependencies.
        
        Args:
            document_repo: Repository for fetching parcel documents
        """
        self.document_repo = document_repo
        
    async def build_parcel_payload(self, parcel: Parcel) -> Dict[str, Any]:
        """
        Build a comprehensive payload for a parcel QR code.
        
        Includes:
        - Parcel identification (number, parish)
        - Ownership details
        - Area and spatial reference
        - Checksums of all active documents (for integrity verification)
        
        Args:
            parcel: Parcel model instance
            
        Returns:
            Dictionary payload for QR encoding
        """
        # Get all active documents for this parcel
        documents = await self.document_repo.get_by_parcel(parcel.id)
        
        # Build document manifest (checksums are key for integrity)
        document_manifest = [
            {
                "type": doc.document_type.code if doc.document_type else "UNKNOWN",
                "ref": doc.reference_number,
                "hash": doc.checksum[:16] # Use truncated hash for QR space efficiency
            }
            for doc in documents if doc.is_active
        ]
        
        payload = {
            "v": "1.0", # Payload version
            "type": "PARCEL",
            "ts": datetime.utcnow().isoformat(),
            "data": {
                "id": str(parcel.id),
                "num": parcel.parcel_number,
                "owner": parcel.owner_name,
                "area": parcel.area_sqm,
                "parish": parcel.parish.name if parcel.parish else "UNKNOWN",
                "docs": document_manifest
            }
        }
        
        return payload

    async def build_document_payload(self, document: Document) -> Dict[str, Any]:
        """
        Build a specific payload for a single document QR code.
        
        Args:
            document: Document model instance
            
        Returns:
            Dictionary payload for QR encoding
        """
        payload = {
            "v": "1.0",
            "type": "DOCUMENT",
            "ts": datetime.utcnow().isoformat(),
            "data": {
                "id": str(document.id),
                "type": document.document_type.code if document.document_type else "UNKNOWN",
                "ref": document.reference_number,
                "filename": document.filename,
                "hash": document.checksum, # Full hash for single document
                "parcel_num": document.parcel.parcel_number if document.parcel else None
            }
        }
        
        return payload
