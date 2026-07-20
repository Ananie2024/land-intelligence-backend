# app/repositories/document_repository.py
"""
Document Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base_repository import BaseRepository
from app.schemas.document_schema import DocumentCreate, DocumentUpdate


class DocumentRepository(BaseRepository[Document, DocumentCreate, DocumentUpdate]):
    """
    Repository for Document entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize document repository.
        
        Args:
            db: Async database session
        """
        super().__init__(Document, db)
    
    async def create(self, schema: DocumentCreate) -> Document:
        """
        Create a document, converting parcel_upi to parcel_id UUID.
        """
        data = schema.model_dump(exclude_none=True)
        
        # Convert parcel_upi to parcel_id if provided
        if "parcel_upi" in data:
            # This should be handled by the service layer
            # For now, we'll just remove parcel_upi as the DB model uses parcel_id
            data.pop("parcel_upi", None)
        
        document = Document(**data)
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def create_direct(self, data: dict) -> Document:
        """
        Create a document directly with raw data dictionary.
        Used when parcel_upi has already been converted to parcel_id.
        
        Args:
            data: Dictionary with document data (parcel_id instead of parcel_upi)
            
        Returns:
            Created document instance
        """
        # Generate UUID if not provided (required since database doesn't have gen_random_uuid)
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())
        document = Document(**data)
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def update(self, id: str, schema: DocumentUpdate) -> Optional[Document]:
        """
        Update a document.
        """
        data = schema.model_dump(exclude_none=True)
        
        # Convert parcel_upi to parcel_id if provided
        if "parcel_upi" in data:
            data.pop("parcel_upi", None)
        
        document = await self.get(id)
        if not document:
            return None
        
        for field, value in data.items():
            if hasattr(document, field):
                setattr(document, field, value)
        
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def get_by_parcel(self, parcel_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Get all documents belonging to a parcel.
        
        Args:
            parcel_id: UUID of the parcel
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of document instances
        """
        return await self.list(
            filters={"parcel_id": parcel_id},
            skip=skip,
            limit=limit
        )
    
    async def get_by_type(self, type_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Get all documents by document type.
        
        Args:
            type_id: UUID of document type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of document instances
        """
        return await self.list(
            filters={"document_type_id": type_id},
            skip=skip,
            limit=limit
        )
    
    async def list_recent(self, limit: int = 10) -> List[Document]:
        """
        Get most recently created documents.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of recent document instances
        """
        result = await self.db.execute(
            select(Document)
            .where(Document.is_active)
            .order_by(desc(Document.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_reference_number(self, reference_number: str) -> Optional[Document]:
        """
        Get document by official reference number.
        
        Args:
            reference_number: Official reference number
            
        Returns:
            Document instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Document).where(
                Document.reference_number == reference_number,
                Document.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_filename(self, filename: str) -> Optional[Document]:
        """
        Get document by filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Document instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Document).where(
                Document.filename == filename,
                Document.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_file_path(self, file_path: str) -> Optional[Document]:
        """
        Get document by file path.
        
        Args:
            file_path: Path to file on filesystem
            
        Returns:
            Document instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Document).where(
                Document.file_path == file_path,
                Document.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_checksum_and_parcel(
        self,
        checksum: str,
        parcel_id: str,
    ) -> Optional[Document]:
        """
        Get a document by checksum within a parcel.
        """
        result = await self.db.execute(
            select(Document).where(
                Document.checksum == checksum,
                Document.parcel_id == parcel_id,
                Document.is_active,
            )
        )
        return result.scalar_one_or_none()
    
    async def search(
        self,
        filename: Optional[str] = None,
        reference_number: Optional[str] = None,
        parcel_id: Optional[str] = None,
        document_type_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        Advanced search with multiple filters.
        
        Args:
            filename: Filter by filename (partial match)
            reference_number: Filter by reference number (partial match)
            parcel_id: Filter by parcel (UUID)
            document_type_id: Filter by document type
            from_date: Filter documents from this date (YYYY-MM-DD)
            to_date: Filter documents up to this date (YYYY-MM-DD)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching document instances
        """
        query = select(Document).where(Document.is_active)
        
        if filename:
            query = query.where(Document.filename.contains(filename))
        
        if reference_number:
            query = query.where(Document.reference_number.contains(reference_number))
        
        if parcel_id:
            query = query.where(Document.parcel_id == parcel_id)
        
        if document_type_id:
            query = query.where(Document.document_type_id == document_type_id)
        
        if from_date:
            query = query.where(Document.document_date >= from_date)
        
        if to_date:
            query = query.where(Document.document_date <= to_date)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_parcel(self, parcel_id: str) -> int:
        """
        Count active documents for a specific parcel.

        Args:
            parcel_id: UUID of the parcel

        Returns:
            Total count of documents for the parcel
        """
        result = await self.db.execute(
            select(func.count(Document.id)).where(
                Document.parcel_id == parcel_id,
                Document.is_active,
            )
        )
        return int(result.scalar_one() or 0)