# app/repositories/document_type_repository.py
"""
Document Type Repository
Phase 2 - Section 3.2
Land Intelligence System
"""

from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_type import DocumentType
from app.repositories.base_repository import BaseRepository


class DocumentTypeRepository(BaseRepository[DocumentType, Any, Any]):
    """
    Repository for DocumentType entity with extended functionality.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize document type repository.

        Args:
            db: Async database session
        """
        super().__init__(DocumentType, db)

    async def get_by_code(self, code: str) -> Optional[DocumentType]:
        """
        Get document type by unique code.

        Args:
            code: Unique document type code

        Returns:
            Document type instance if found, None otherwise
        """
        result = await self.db.execute(
            select(DocumentType).where(
                DocumentType.code == code,
                DocumentType.is_active,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[DocumentType]:
        """
        Get document type by unique name.

        Args:
            name: Document type name

        Returns:
            Document type instance if found, None otherwise
        """
        result = await self.db.execute(
            select(DocumentType).where(
                DocumentType.name == name,
                DocumentType.is_active,
            )
        )
        return result.scalar_one_or_none()

    async def list_requiring_verification(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentType]:
        """
        List active document types that require verification.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of document type instances
        """
        result = await self.db.execute(
            select(DocumentType)
            .where(
                DocumentType.requires_verification,
                DocumentType.is_active,
            )
            .order_by(DocumentType.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_name(
        self,
        name: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentType]:
        """
        Search document types by name.

        Args:
            name: Partial document type name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching document type instances
        """
        result = await self.db.execute(
            select(DocumentType)
            .where(
                DocumentType.name.contains(name),
                DocumentType.is_active,
            )
            .order_by(DocumentType.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
