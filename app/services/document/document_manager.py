"""
Document Manager Service
Phase 3 — Section 4.1
Land Intelligence System
"""

import uuid
from typing import Optional, List, BinaryIO, Any

from app.repositories.document_repository import DocumentRepository
from app.repositories.document_type_repository import DocumentTypeRepository
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.qr_registry_repository import QRRegistryRepository
from app.schemas.document_schema import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.document.file_system_handler import FileSystemHandler
from app.services.document.metadata_extractor import MetadataExtractor
from app.services.document.pointer_resolver import PointerResolver


class DocumentManager:
    """
    Orchestrates document CRUD operations.
    
    Coordinates between repositories, file system, metadata extraction,
    and physical location resolution.
    """
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        document_type_repo: DocumentTypeRepository,
        parcel_repo: ParcelRepository,
        file_handler: FileSystemHandler,
        metadata_extractor: MetadataExtractor,
        pointer_resolver: PointerResolver,
        qr_repo: Optional[QRRegistryRepository] = None
    ):
        """
        Initialize document manager with dependencies.
        
        Args:
            document_repo: Document repository
            document_type_repo: Document type repository
            parcel_repo: Parcel repository
            file_handler: File system handler
            metadata_extractor: Metadata extractor
            pointer_resolver: Pointer resolver
            qr_repo: QR registry repository (optional, for QR code integration)
        """
        self.document_repo = document_repo
        self.document_type_repo = document_type_repo
        self.parcel_repo = parcel_repo
        self.file_handler = file_handler
        self.metadata_extractor = metadata_extractor
        self.pointer_resolver = pointer_resolver
        self.qr_repo = qr_repo
    
    async def _resolve_document_type(self, document_type_id_or_code: str) -> Optional[Any]:
        """
        Resolve document type by UUID or code.
        
        Args:
            document_type_id_or_code: Either a UUID or a document type code
            
        Returns:
            Document type instance if found, None otherwise
        """
        # Try to parse as UUID first
        try:
            uuid.UUID(document_type_id_or_code)
            # It's a valid UUID, look up by ID
            return await self.document_type_repo.get(document_type_id_or_code)
        except (ValueError, TypeError):
            # Not a valid UUID, try to look up by code
            return await self.document_type_repo.get_by_code(document_type_id_or_code)

    async def create_document(
        self,
        file: BinaryIO,
        filename: str,
        metadata: DocumentCreate,
        user_id: str
    ) -> DocumentResponse:
        """
        Create a new document with file upload.
        
        Args:
            file: File binary stream
            filename: Original filename
            metadata: Document metadata
            user_id: ID of user creating document
            
        Returns:
            Created document response
            
        Raises:
            ValueError: If document type not found, parcel not found, or duplicate file
        """
        # Validate document type exists (accepts UUID or code)
        doc_type = await self._resolve_document_type(metadata.document_type_id)
        if not doc_type:
            raise ValueError(f"Document type {metadata.document_type_id} not found")
        
        # Validate parcel exists if provided (using UPI format)
        parcel_id = None
        if metadata.parcel_upi:
            parcel = await self.parcel_repo.get_by_upi(metadata.parcel_upi)
            if not parcel:
                raise ValueError(f"Parcel with UPI {metadata.parcel_upi} not found")
            parcel_id = str(parcel.id)
        
        # Extract metadata from file
        file_metadata = await self.metadata_extractor.extract(file, filename)
        
        # Validate file type and size
        file_size_bytes = file_metadata.get("file_size_bytes", 0)
        if not self.metadata_extractor.validate_file_type(filename):
            raise ValueError("Unsupported file type")
        if not self.metadata_extractor.validate_file_size(file_size_bytes):
            raise ValueError("File size exceeds limit")
        
        # Check for duplicate file using checksum
        checksum = file_metadata.get("checksum")
        if checksum and parcel_id:
            existing = await self.document_repo.get_by_checksum_and_parcel(
                checksum, parcel_id
            )
            if existing:
                raise ValueError("Duplicate document: same file already exists for this parcel")
        
        # Reset file stream to beginning for save operation
        # Extract operation may have consumed the stream
        file.seek(0)
        
        # Save file to filesystem
        file_path = await self.file_handler.save_file(file, filename, parcel_id)
        
        # Create document record - use the resolved document type's UUID
        document_kwargs = {
            "document_type_id": str(doc_type.id),
            "filename": filename,
            "file_path": str(file_path),
            "file_size_bytes": file_metadata.get("file_size_bytes", 0),
            "mime_type": file_metadata.get("mime_type", "application/octet-stream"),
            "checksum": file_metadata.get("checksum", ""),
            "description": metadata.description,
            "document_date": metadata.document_date,
            "reference_number": metadata.reference_number,
            "page_count": file_metadata.get("page_count"),
        }
        
        # We need to add parcel_id separately since the DB model uses it
        # Store the parcel_id if we have it
        if parcel_id:
            document_kwargs["parcel_id"] = parcel_id
        
        try:
            document = await self.document_repo.create_direct(document_kwargs)
        except Exception as e:
            # Database creation failed - clean up the saved file
            await self.file_handler.delete_file(str(file_path))
            raise e
        
        return DocumentResponse.model_validate(document)
    
    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """
        Get document by ID.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document response if found, None otherwise
        """
        document = await self.document_repo.get(document_id)
        if not document:
            return None
        
        # Build response data
        response_data = {
            "id": str(document.id),
            "document_type_id": str(document.document_type_id),
            "parcel_upi": document.parcel.upi if document.parcel else None,
            "filename": document.filename,
            "file_path": document.file_path,
            "file_size_bytes": document.file_size_bytes,
            "mime_type": document.mime_type,
            "description": document.description,
            "document_date": document.document_date,
            "reference_number": document.reference_number,
            "page_count": document.page_count,
            "checksum": document.checksum,
            "is_active": document.is_active,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
            "extra_data": document.extra_data,
            # Document type and QR code count
            "document_type_name": document.document_type.name if document.document_type else None,
            "qr_code_count": await self._get_qr_code_count(document_id) if self.qr_repo else 0,
        }
        
        return DocumentResponse(**response_data)
    
    async def _get_qr_code_count(self, document_id: str) -> int:
        """
        Get the count of active QR codes for a document.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Count of active QR codes for this document
        """
        if not self.qr_repo:
            return 0
        return await self.qr_repo.count_by_document(document_id)
    
    async def get_document_with_file(self, document_id: str) -> Optional[tuple]:
        """
        Get document with file stream.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Tuple of (document, file_stream) if found, None otherwise
        """
        document = await self.document_repo.get(document_id)
        if not document:
            return None
        
        file_stream = await self.file_handler.get_file(document.file_path)
        if not file_stream:
            return None
        
        return (document, file_stream)
    
    async def update_document(
        self,
        document_id: str,
        update_data: DocumentUpdate,
        user_id: str
    ) -> Optional[DocumentResponse]:
        """
        Update document metadata.
        
        Args:
            document_id: Document UUID
            update_data: Updated metadata
            user_id: ID of user updating document
            
        Returns:
            Updated document response if found, None otherwise
        """
        # Resolve document_type_id to UUID if it's a code
        update_dict = update_data.model_dump(exclude_none=True)
        if "document_type_id" in update_dict:
            doc_type = await self._resolve_document_type(update_dict["document_type_id"])
            if doc_type:
                update_dict["document_type_id"] = str(doc_type.id)
        
        # Reconstruct update_data with resolved document_type_id
        update_data = DocumentUpdate(**update_dict)
        
        document = await self.document_repo.update(document_id, update_data)
        if not document:
            return None
        
        return DocumentResponse.model_validate(document)
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Soft delete a document.
        
        Args:
            document_id: Document UUID
            user_id: ID of user deleting document
            
        Returns:
            True if deleted, False if not found
        """
        return await self.document_repo.soft_delete(document_id)
    
    async def hard_delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Permanently delete a document (including file).
        
        Args:
            document_id: Document UUID
            user_id: ID of user deleting document
            
        Returns:
            True if deleted, False if not found
        """
        document = await self.document_repo.get(document_id)
        if not document:
            return False
        
        # Delete file from filesystem
        await self.file_handler.delete_file(document.file_path)
        
        # Hard delete from database
        return await self.document_repo.hard_delete(document_id)
    
    async def list_documents_by_parcel(
        self,
        parcel_upi: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentResponse]:
        """
        List documents belonging to a parcel.
        
        Args:
            parcel_upi: Unique Parcel Identifier (UPI) - e.g. 1/02/02/03/1390
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of document responses
        """
        # Get parcel by UPI first
        parcel = await self.parcel_repo.get_by_upi(parcel_upi)
        if not parcel:
            return []
        
        documents = await self.document_repo.get_by_parcel(str(parcel.id), skip, limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]
    
    async def list_documents_by_type(
        self,
        type_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentResponse]:
        """
        List documents by type.
        
        Args:
            type_id: Document type UUID or code
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of document responses
        """
        # Resolve type_id to UUID if it's a code
        resolved_type = await self._resolve_document_type(type_id)
        actual_type_id = str(resolved_type.id) if resolved_type else type_id
        
        documents = await self.document_repo.get_by_type(actual_type_id, skip, limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]
    
    async def list_recent_documents(self, limit: int = 10) -> List[DocumentResponse]:
        """
        List most recent documents.
        
        Args:
            limit: Maximum number of documents
            
        Returns:
            List of document responses
        """
        documents = await self.document_repo.list_recent(limit)
        return [DocumentResponse.model_validate(doc) for doc in documents]
    
    async def search_documents(
        self,
        filename: Optional[str] = None,
        reference_number: Optional[str] = None,
        parcel_upi: Optional[str] = None,
        document_type_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentResponse]:
        """
        Search documents with filters.
        
        Args:
            filename: Filter by filename (partial match)
            reference_number: Filter by reference number
            parcel_upi: Filter by Unique Parcel Identifier (UPI)
            document_type_id: Filter by document type (UUID or code)
            from_date: Filter from date
            to_date: Filter to date
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of document responses
        """
        # Convert UPI to parcel_id if provided
        parcel_id = None
        if parcel_upi:
            parcel = await self.parcel_repo.get_by_upi(parcel_upi)
            if parcel:
                parcel_id = str(parcel.id)
        
        # Resolve document_type_id to UUID if it's a code
        actual_type_id = None
        if document_type_id:
            resolved_type = await self._resolve_document_type(document_type_id)
            if resolved_type:
                actual_type_id = str(resolved_type.id)
        
        documents = await self.document_repo.search(
            filename=filename,
            reference_number=reference_number,
            parcel_id=parcel_id,
            document_type_id=actual_type_id,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit
        )
        return [DocumentResponse.model_validate(doc) for doc in documents]
    
    async def resolve_physical_location(self, document_id: str) -> Optional[dict]:
        """
        Resolve physical location for a document.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Physical location info if found, None otherwise
        """
        document = await self.document_repo.get(document_id)
        if not document:
            return None
        
        return await self.pointer_resolver.resolve_with_cabinet(document)