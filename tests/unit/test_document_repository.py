# tests/unit/test_document_repository.py
"""
Unit tests for DocumentRepository.
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository


@pytest.fixture
def mock_db():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def doc_repo(mock_db):
    return DocumentRepository(mock_db)


def _make_document(
    id: str = "doc-uuid-1",
    parcel_id: str = "parcel-uuid-1",
    document_type_id: str = "type-uuid-1",
    filename: str = "test.pdf",
    file_path: str = "/uploads/test.pdf",
    file_size_bytes: int = 1024,
    mime_type: str = "application/pdf",
    checksum: str = "abc123def456",
    reference_number: str = None,
    is_active: bool = True,
):
    doc = MagicMock(spec=Document)
    doc.id = id
    doc.parcel_id = parcel_id
    doc.document_type_id = document_type_id
    doc.filename = filename
    doc.file_path = file_path
    doc.file_size_bytes = file_size_bytes
    doc.mime_type = mime_type
    doc.checksum = checksum
    doc.reference_number = reference_number
    doc.is_active = is_active
    doc.description = None
    doc.document_date = None
    doc.page_count = None
    return doc


class TestDocumentRepository:
    async def test_create_document(self, doc_repo, mock_db):
        from app.schemas.document_schema import DocumentCreate
        
        schema = DocumentCreate(
            parcel_id="parcel-uuid-1",
            document_type_id="type-uuid-1",
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            checksum="abc123",
        )
        
        doc = await doc_repo.create(schema)
        assert doc is not None
        mock_db.add.assert_called()
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    async def test_update_document(self, doc_repo, mock_db):
        existing = _make_document()
        doc_repo.get = AsyncMock(return_value=existing)
        
        from app.schemas.document_schema import DocumentUpdate
        update = DocumentUpdate(filename="updated.pdf", description="Updated doc")
        
        result = await doc_repo.update("doc-uuid-1", update)
        assert result is existing
        assert result.filename == "updated.pdf"
        assert result.description == "Updated doc"
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    async def test_update_nonexistent_returns_none(self, doc_repo, mock_db):
        doc_repo.get = AsyncMock(return_value=None)
        
        from app.schemas.document_schema import DocumentUpdate
        update = DocumentUpdate(filename="updated.pdf")
        
        result = await doc_repo.update("nonexistent-id", update)
        assert result is None
        mock_db.flush.assert_not_called()

    async def test_get_by_parcel(self, doc_repo, mock_db):
        docs = [_make_document(id=f"doc-{i}") for i in range(3)]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.get_by_parcel("parcel-uuid-1", skip=0, limit=10)
        assert len(result) == 3

    async def test_get_by_type(self, doc_repo, mock_db):
        docs = [_make_document(id=f"doc-{i}") for i in range(2)]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.get_by_type("type-uuid-1")
        assert len(result) == 2

    async def test_list_recent(self, doc_repo, mock_db):
        docs = [_make_document(id=f"doc-{i}") for i in range(5)]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.list_recent(limit=5)
        assert len(result) == 5

    async def test_get_by_reference_number(self, doc_repo, mock_db):
        doc = _make_document(reference_number="REF-123")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.get_by_reference_number("REF-123")
        assert result is doc

    async def test_get_by_filename(self, doc_repo, mock_db):
        doc = _make_document(filename="unique.pdf")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.get_by_filename("unique.pdf")
        assert result is doc

    async def test_get_by_file_path(self, doc_repo, mock_db):
        doc = _make_document(file_path="/uploads/test.pdf")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.get_by_file_path("/uploads/test.pdf")
        assert result is doc

    async def test_get_by_checksum_and_parcel(self, doc_repo, mock_db):
        doc = _make_document(checksum="abc123", parcel_id="parcel-1")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.get_by_checksum_and_parcel("abc123", "parcel-1")
        assert result is doc

    async def test_search_by_filename(self, doc_repo, mock_db):
        docs = [_make_document(filename="report.pdf")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.search(filename="report")
        assert len(result) == 1
        assert result[0].filename == "report.pdf"

    async def test_search_by_reference_number(self, doc_repo, mock_db):
        docs = [_make_document(reference_number="REF-999")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.search(reference_number="REF-999")
        assert len(result) == 1

    async def test_search_by_parcel_id(self, doc_repo, mock_db):
        docs = [_make_document(parcel_id="parcel-123")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.search(parcel_id="parcel-123")
        assert len(result) == 1

    async def test_search_by_document_type(self, doc_repo, mock_db):
        docs = [_make_document(document_type_id="type-456")]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.search(document_type_id="type-456")
        assert len(result) == 1

    async def test_search_by_date_range(self, doc_repo, mock_db):
        docs = [_make_document()]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.search(from_date="2024-01-01", to_date="2024-12-31")
        assert len(result) == 1

    async def test_search_with_pagination(self, doc_repo, mock_db):
        docs = [_make_document(id=f"doc-{i}") for i in range(10)]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = docs
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result
        
        result = await doc_repo.search(skip=5, limit=5)
