import uuid
import sys
import os
sys.path.insert(0, os.getcwd())

from app.models.document import Document
from app.schemas.document_schema import DocumentResponse

# Test 1: Object with extra_data attribute (correct)
class CorrectMock:
    def __init__(self):
        self.id = uuid.uuid4()
        self.document_type_id = uuid.uuid4()
        self.filename = 'test.pdf'
        self.file_path = '/uploads/test.pdf'
        self.file_size_bytes = 1000
        self.mime_type = 'application/pdf'
        self.checksum = 'abc123'
        self.is_active = True
        self.created_at = '2024-01-01T00:00:00'
        self.updated_at = '2024-01-01T00:00:00'
        self.extra_data = {'test': 'value'}  # Python attribute

correct = CorrectMock()
try:
    resp = DocumentResponse.model_validate(correct)
    print(f"Test 1 (extra_data attr): SUCCESS - extra_data={resp.extra_data}")
except Exception as e:
    print(f"Test 1 FAILED: {e}")

# Test 2: Object with metadata attribute only (simulating SQLAlchemy column name access)
class MetadataAttrMock:
    def __init__(self):
        self.id = uuid.uuid4()
        self.document_type_id = uuid.uuid4()
        self.filename = 'test.pdf'
        self.file_path = '/uploads/test.pdf'
        self.file_size_bytes = 1000
        self.mime_type = 'application/pdf'
        self.checksum = 'abc123'
        self.is_active = True
        self.created_at = '2024-01-01T00:00:00'
        self.updated_at = '2024-01-01T00:00:00'
        self.metadata = {'test': 'value'}  # DB column name

metadata_attr = MetadataAttrMock()
try:
    resp = DocumentResponse.model_validate(metadata_attr)
    print(f"Test 2 (metadata attr): SUCCESS - extra_data={resp.extra_data}")
except Exception as e:
    print(f"Test 2 FAILED: {e}")

# Test 3: Object with NO metadata or extra_data attribute (None case)
class NoMetaAttrMock:
    def __init__(self):
        self.id = uuid.uuid4()
        self.document_type_id = uuid.uuid4()
        self.filename = 'test.pdf'
        self.file_path = '/uploads/test.pdf'
        self.file_size_bytes = 1000
        self.mime_type = 'application/pdf'
        self.checksum = 'abc123'
        self.is_active = True
        self.created_at = '2024-01-01T00:00:00'
        self.updated_at = '2024-01-01T00:00:00'

no_meta = NoMetaAttrMock()
try:
    resp = DocumentResponse.model_validate(no_meta)
    print(f"Test 3 (no metadata attr): SUCCESS - extra_data={resp.extra_data}")
except Exception as e:
