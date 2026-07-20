# QR Module Extension Plan - COMPLETED
- [x] Analyze current QR module implementation and identify limitations
- [x] Fix `get_by_document` method indentation bug in qr_registry_repository.py
- [x] Add QR code generation endpoint to document routes
- [x] Add QR code retrieval endpoint to document routes
- [x] Populate qr_code_count in DocumentResponse
- [x] Add QR code count repository method
- [x] Update frontend DocumentDetail component with QR code functionality
- [x] Update QR Codes page to support document type dropdown and document dropdown selection
- [x] Add documentService.getDocumentsByType method for fetching documents by type

## Summary of Changes

### Backend Changes

#### 1. QR Registry Repository (`app/repositories/qr_registry_repository.py`)
- Fixed indentation bug in `get_by_document` method
- Added `get_all_by_document` method
- Added `count_by_document` method

#### 2. QR Service (`app/services/qr/qr_service.py`)
- Fixed `generate_parcel_qr` to use `get_by_upi` method
- Fixed `generate_document_qr` to use `extra_data` instead of `metadata`
- Added `get_qr_details_by_document` method

#### 3. Document Manager (`app/services/document/document_manager.py`)
- Added optional `qr_repo` parameter
- Updated `get_document` to populate `qr_code_count`
- Added `_get_qr_code_count` helper method

#### 4. Document Routes (`app/api/v1/routes/documents.py`)
- Added `POST /documents/{document_id}/qr-code` endpoint
- Added `GET /documents/{document_id}/qr-code` endpoint

### Frontend Changes

#### 1. API Endpoints (`land-intelligence-frontend/src/api/endpoints.ts`)
- Added `DOCUMENT_QR` endpoints

#### 2. QR Service (`land-intelligence-frontend/src/services/qrService.ts`)
- Added `documentQrService` with `generateQrCode` and `getQrCode` methods

#### 3. Document Service (`land-intelligence-frontend/src/services/documentService.ts`)
- Added `getDocumentsByType` method for fetching documents by type code

#### 4. Document Types (`land-intelligence-frontend/src/types/document.ts`)
- Fixed `DOCUMENT_TYPE_LABELS.cession` key

#### 5. DocumentDetail Component (`land-intelligence-frontend/src/features/documents/components/DocumentDetail.tsx`)
- Added QR code section with generation button

#### 6. QrCodes Page (`land-intelligence-frontend/src/pages/QrCodes.tsx`)
- Tabs to switch between Parcel QR and Document QR
- Document type dropdown (Land Titles, Land Deeds, Letters, etc.)
- Document dropdown (populated when type is selected)
- Generate QR code button for selected document

## How It Works Now
1. User clicks "Document QR" tab
2. User selects a document type from the dropdown (e.g., "Letters")
3. All documents of that type are loaded into the second dropdown
4. User selects a document from the dropdown
5. User clicks "Generate QR Code" button
6. QR code is generated for that document