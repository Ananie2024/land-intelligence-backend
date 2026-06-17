# app/api/v1/routes/documents.py

"""
Document Management API Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_data, get_current_user_id
from app.schemas.document_schema import (
    DocumentResponse, 
    DocumentUploadRequest, 
    DocumentUpdate,
    DocumentListResponse,
    DocumentSearchParams
)
from app.services.document.document_manager import DocumentManager
from app.services.document.file_system_handler import FileSystemHandler
from app.services.document.metadata_extractor import MetadataExtractor
from app.services.document.pointer_resolver import PointerResolver
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_type_repository import DocumentTypeRepository
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.location_repository import LocationRepository
from app.schemas.document_schema import DocumentCreate

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_document_manager(db: AsyncSession = Depends(get_db)) -> DocumentManager:
    """Dependency to provide DocumentManager instance."""
    return DocumentManager(
        document_repo=DocumentRepository(db),
        document_type_repo=DocumentTypeRepository(db),
        parcel_repo=ParcelRepository(db),
        file_handler=FileSystemHandler(),
        metadata_extractor=MetadataExtractor(),
        pointer_resolver=PointerResolver(LocationRepository(db))
    )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    parcel_id: Optional[str] = Form(None),
    document_type_id: str = Form(...),
    description: Optional[str] = Form(None),
    document_date: Optional[str] = Form(None),
    reference_number: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """
    Upload a document with metadata.
    """
    try:
        # Create metadata object from form data
        metadata = DocumentCreate(
            parcel_id=parcel_id,
            document_type_id=document_type_id,
            description=description,
            document_date=document_date,
            reference_number=reference_number,
            filename=file.filename or "unknown"
        )
        
        return await doc_manager.create_document(
            file=file.file,
            filename=file.filename or "unknown",
            metadata=metadata,
            user_id=user_id
        )
    except ValueError as e:
        logger.warning(f"Document upload validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during document upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document upload"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Get document metadata by ID."""
    document = await doc_manager.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    return document


@router.get("/{document_id}/file")
async def download_document(
    document_id: str,
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Download document file."""
    result = await doc_manager.get_document_with_file(document_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found or file missing"
        )
    
    document, file_stream = result
    
    # aiofiles stream needs to be used in StreamingResponse
    return StreamingResponse(
        file_stream,
        media_type=document.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{document.filename}"'
        }
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    user_id: str = Depends(get_current_user_id),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Update document metadata."""
    document = await doc_manager.update_document(document_id, update_data, user_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    hard_delete: bool = Query(False, description="Permanently delete file and record"),
    user_id: str = Depends(get_current_user_id),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Delete a document."""
    if hard_delete:
        success = await doc_manager.hard_delete_document(document_id, user_id)
    else:
        success = await doc_manager.delete_document(document_id, user_id)
        
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    return None


@router.get("/", response_model=DocumentListResponse)
async def search_documents(
    parcel_id: Optional[str] = None,
    document_type_id: Optional[str] = None,
    filename: Optional[str] = None,
    reference_number: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Search and list documents with pagination."""
    skip = (page - 1) * size
    
    # Note: list/search implementation depends on repository capabilities
    # This is a simplified search implementation
    documents = await doc_manager.search_documents(
        filename=filename,
        reference_number=reference_number,
        parcel_id=parcel_id,
        document_type_id=document_type_id,
        skip=skip,
        limit=size
    )
    
    # We'd need a separate count method for true pagination response
    # For now, we return the list. In a real scenario, we'd wrap this.
    return DocumentListResponse(
        items=documents,
        total=len(documents), # Simplified
        page=page,
        size=size,
        pages=1 # Simplified
    )


@router.get("/{document_id}/physical-location")
async def get_physical_location(
    document_id: str,
    doc_manager: DocumentManager = Depends(get_document_manager)
):
    """Resolve physical location for a document."""
    location = await doc_manager.resolve_physical_location(document_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Physical location for document {document_id} not found"
        )
    return location
