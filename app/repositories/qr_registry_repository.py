# app/repositories/qr_registry_repository.py
"""
QR Code Registry Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.qr_code_registry import QRCodeRegistry
from app.repositories.base_repository import BaseRepository
from app.schemas.qr_code_schema import QRCodeCreate, QRCodeUpdate


class QRRegistryRepository(BaseRepository[QRCodeRegistry, QRCodeCreate, QRCodeUpdate]):
    """
    Repository for QRCodeRegistry entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize QR registry repository.
        
        Args:
            db: Async database session
        """
        super().__init__(QRCodeRegistry, db)
    
    async def get_by_code(self, qr_string: str) -> Optional[QRCodeRegistry]:
        """
        Get QR code registry entry by QR code string.
        
        Args:
            qr_string: Unique QR code string
            
        Returns:
            QR code registry entry if found, None otherwise
        """
        result = await self.db.execute(
            select(QRCodeRegistry).where(
                QRCodeRegistry.code == qr_string,
                QRCodeRegistry.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_parcel(self, parcel_id: str) -> List[QRCodeRegistry]:
        """
        Get all QR codes for a parcel.
        
        Args:
            parcel_id: UUID of the parcel
            
        Returns:
            List of QR code registry entries
        """
        result = await self.db.execute(
            select(QRCodeRegistry).where(
                QRCodeRegistry.parcel_id == parcel_id,
                QRCodeRegistry.is_active == True
            ).order_by(desc(QRCodeRegistry.created_at))
        )
        return list(result.scalars().all())
    
    async def get_by_document(self, document_id: str) -> Optional[QRCodeRegistry]:
        """
        Get QR code for a document.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            QR code registry entry if found, None otherwise
        """
        result = await self.db.execute(
            select(QRCodeRegistry).where(
                QRCodeRegistry.document_id == document_id,
                QRCodeRegistry.is_active == True
            ).order_by(desc(QRCodeRegistry.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_valid_code(self, qr_string: str) -> Optional[QRCodeRegistry]:
        """
        Get QR code entry only if it's valid (not revoked, not expired).
        
        Args:
            qr_string: Unique QR code string
            
        Returns:
            QR code registry entry if valid, None otherwise
        """
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            select(QRCodeRegistry).where(
                QRCodeRegistry.code == qr_string,
                QRCodeRegistry.is_active == True,
                QRCodeRegistry.is_revoked == False,
                or_(
                    QRCodeRegistry.expires_at.is_(None),
                    QRCodeRegistry.expires_at > now
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def revoke_code(self, qr_string: str) -> Optional[QRCodeRegistry]:
        """
        Revoke a QR code (mark as invalid).
        
        Args:
            qr_string: Unique QR code string
            
        Returns:
            Updated QR code registry entry, None if not found
        """
        entry = await self.get_by_code(qr_string)
        if entry:
            entry.is_revoked = True
            await self.db.flush()
            await self.db.refresh(entry)
        return entry
    
    async def record_access(self, qr_string: str) -> Optional[QRCodeRegistry]:
        """
        Record that a QR code was accessed/scanned.
        
        Args:
            qr_string: Unique QR code string
            
        Returns:
            Updated QR code registry entry, None if not found
        """
        entry = await self.get_by_code(qr_string)
        if entry:
            entry.last_accessed_at = datetime.now(timezone.utc)
            entry.access_count += 1
            await self.db.flush()
            await self.db.refresh(entry)
        return entry
    
    async def list_active_by_parcel(self, parcel_id: str) -> List[QRCodeRegistry]:
        """
        List active (non-revoked, non-expired) QR codes for a parcel.
        
        Args:
            parcel_id: UUID of the parcel
            
        Returns:
            List of active QR code registry entries
        """
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            select(QRCodeRegistry).where(
                QRCodeRegistry.parcel_id == parcel_id,
                QRCodeRegistry.is_active == True,
                QRCodeRegistry.is_revoked == False,
                or_(
                    QRCodeRegistry.expires_at.is_(None),
                    QRCodeRegistry.expires_at > now
                )
            ).order_by(desc(QRCodeRegistry.created_at))
        )
        return list(result.scalars().all())
    
    async def cleanup_expired(self) -> int:
        """
        Soft delete expired QR codes.
        
        Returns:
            Number of expired codes cleaned up
        """
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            select(QRCodeRegistry).where(
                QRCodeRegistry.is_active == True,
                QRCodeRegistry.expires_at.is_not(None),
                QRCodeRegistry.expires_at <= now
            )
        )
        expired_codes = result.scalars().all()
        
        count = 0
        for code in expired_codes:
            code.is_active = False
            count += 1
        
        await self.db.flush()
        return count
