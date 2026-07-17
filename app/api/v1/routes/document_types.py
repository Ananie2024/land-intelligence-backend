# app/api/v1/routes/document_types.py
"""
Document Type Management API Routes
Land Intelligence System
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.document_type_repository import DocumentTypeRepository
from app.schemas.document_type_schema import DocumentTypeResponse, DocumentTypeListResponse
from app.api.auth_dependencies import get_current_user_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=DocumentTypeListResponse, include_in_schema=False)
async def list_document_types(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_data),
):
    """List all document types with pagination (no trailing slash)."""
    repository = DocumentTypeRepository(db)
    skip = (page - 1) * size
    
    type_models = await repository.list(skip=skip, limit=size)
    total = await repository.count()
    
    type_responses = [DocumentTypeResponse.model_validate(dt) for dt in type_models]
    
    pages = (total + size - 1) // size if size else 1
    
    return DocumentTypeListResponse(
        items=type_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/", response_model=DocumentTypeListResponse)
async def list_document_types_slash(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_data),
):
    """List all document types with pagination."""
    repository = DocumentTypeRepository(db)
    skip = (page - 1) * size
    
    type_models = await repository.list(skip=skip, limit=size)
    total = await repository.count()
    
    type_responses = [DocumentTypeResponse.model_validate(dt) for dt in type_models]
    
    pages = (total + size - 1) // size if size else 1
    
    return DocumentTypeListResponse(
        items=type_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{document_type_id}", response_model=DocumentTypeResponse)
async def get_document_type(
    document_type_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_data),
):
    """Get document type by ID."""
    repository = DocumentTypeRepository(db)
    doc_type = await repository.get(document_type_id)
    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type {document_type_id} not found"
        )
    return DocumentTypeResponse.model_validate(doc_type)