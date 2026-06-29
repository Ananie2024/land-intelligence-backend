"""
Document Manager Service
Phase 3 — Section 4.1
Land Intelligence System
"""

from typing import Optional, List, BinaryIO

from app.repositories.document_repository import DocumentRepository
from app.repositories.document_type_repository import DocumentTypeRepository
from app.repositories.parcel_repository import ParcelRepository
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
        pointer_resolver: PointerResolver
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
        """
        self.document_repo = document_repo
        self.document_type_repo = document_type_repo
        self.parcel_repo = parcel_repo
        self.file_handler = file_handler
        self.metadata_extractor = metadata_extractor
        self.pointer_resolver = pointer_resolver
    
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
        # Validate document type exists
        doc_type = await self.document_type_repo.get(metadata.document_type_id)
        if not doc_type:
            raise ValueError(f"Document type {metadata.document_type_id} not found")
        
        # Validate parcel exists if provided
        if metadata.parcel_id:
            parcel = await self.parcel_repo.get(metadata.parcel_id)
            if not parcel:
                raise ValueError(f"Parcel {metadata.parcel_id} not found")
        
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
        if checksum and metadata.parcel_id:
            existing = await self.document_repo.get_by_checksum_and_parcel(
                checksum, metadata.parcel_id
            )
            if existing:
                raise ValueError("Duplicate document: same file already exists for this parcel")
        
        # Reset file stream to beginning for save operation
        # Extract operation may have consumed the stream
        file.seek(0)
        
        # Save file to filesystem
        file_path = await self.file_handler.save_file(file, filename, metadata.parcel_id)
        
        # Create document record
        document_data = DocumentCreate(
            parcel_id=metadata.parcel_id,
            document_type_id=metadata.document_type_id,
            filename=filename,
            file_path=str(file_path),
            file_size_bytes=file_metadata.get("file_size_bytes", 0),
            mime_type=file_metadata.get("mime_type", "application/octet-stream"),
            checksum=file_metadata.get("checksum", ""),
            description=metadata.description,
            document_date=metadata.document_date,
            reference_number=metadata.reference_number,
            page_count=file_metadata.get("page_count"),
        )
        
        try:
            document = await self.document_repo.create(document_data)
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
        
        return DocumentResponse.model_validate(document)
    
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
        parcel_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentResponse]:
        """
        List documents belonging to a parcel.
        
        Args:
            parcel_id: Parcel UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of document responses
        """
        documents = await self.document_repo.get_by_parcel(parcel_id, skip, limit)
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
            type_id: Document type UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of document responses
        """
        documents = await self.document_repo.get_by_type(type_id, skip, limit)
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
        parcel_id: Optional[str] = None,
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
            parcel_id: Filter by parcel
            document_type_id: Filter by document type
            from_date: Filter from date
            to_date: Filter to date
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of document responses
        """
        documents = await self.document_repo.search(
            filename=filename,
            reference_number=reference_number,
            parcel_id=parcel_id,
            document_type_id=document_type_id,
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
