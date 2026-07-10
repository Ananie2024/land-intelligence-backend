# API Integration Layer - Complete Documentation

## Overview
This document describes the complete API integration layer between the frontend and backend.

## Architecture

```
Frontend (Vite/React)          Backend (FastAPI/Python)
====================          ======================
src/api/axios.ts         <---> app/api/middleware/
  - Axios client          exception_handler.py
  - Request interceptor      response_middleware.py
  - Response interceptor
  - Token refresh logic

src/api/apiClient.ts          Standardized APIResponse<T>
  - get<T>()              <--->  (success, data, message, errors, meta, timestamp)

src/api/endpoints.ts          All routes in app/api/v1/routes/
  - ENDPOINTS constants

src/services/*.ts             Backend service layer
  - authService.ts        <---> app/services/auth/auth_service.py
  - landService.ts        <---> app/services/parish/*.py
  - userService.ts        <--->                    \
  - documentService.ts    <--->                     > parcel/*.py, document/*.py
  - qrService.ts          <--->                    /
  - backupService.ts    ...
  - dashboardService.ts
  - locationService.ts
  - reportService.ts
  - projectService.ts
```

## Standardized Response Format

All backend endpoints return a standardized JSON structure:

```typescript
interface APIResponse<T> {
  success: boolean;       // true for successful requests
  data: T | null;         // Response payload
  message: string | null; // Human-readable message
  errors: ErrorDetail[] | null; // Validation/business errors
  meta: PaginationMeta | null;  // Pagination info
  timestamp: string;      // ISO 8601 timestamp
}
```

## Axios Client Features (axios.ts)

### Request Interceptor
- Automatically attaches Bearer token from localStorage to requests
- Removes Content-Type header for FormData (allows browser to set multipart boundary)
- Logs requests in debug mode

### Response Interceptor
- **Token Refresh**: Automatically handles 401 errors by:
  1. Checking if refresh is already in progress
  2. Queueing failed requests during refresh
  3. Calling `/auth/refresh` with refresh token
  4. Retrying original request with new token
  5. Dispatching `auth:unauthorized` event on refresh failure
- **Error Handling**: Converts backend errors to `ApiError` instances
- **Network Errors**: Handles connection failures gracefully

### ApiError Class
Custom error class with structured error details:
```typescript
class ApiError extends Error {
  success: boolean;
  errors: ErrorDetail[] | null;
  meta: PaginationMeta | null;
  timestamp: string;
  status: number;
}
```

## React Query Integration (queryClient.ts)

- Configured with 5-minute stale time, 10-minute cache time
- No retry on 401/403/404 errors
- Global error toasts for failed queries/mutations
- Automatic token refresh handling prevents error toast spam

## Services Status

| Service | Status | Backend Coverage | Notes |
|---------|--------|------------------|-------|
| authService | ✅ Complete | ✅ Full | Login, register, refresh, logout, me, change-password |
| landService | ✅ Complete | ✅ Full | Parishes + Parcels, including map endpoint |
| userService | ✅ Complete | ✅ Full | List, get, update, delete users |
| documentService | ✅ Complete | ✅ Full | Upload, download, CRUD operations |
| qrService | ✅ Updated | ✅ Full | Generate, verify, revoke for parcels/documents |
| backupService | ✅ Updated | ✅ Full | Trigger, restore, job status |
| dashboardService | ✅ Complete | ✅ Full | System stats, parish/parcel/user stats |
| locationService | ✅ New | ✅ Full | Physical locations and cabinets |
| reportService | ✅ Complete | ✅ Full | Tax reports, GIS analysis |
| projectService | ⏳ Pending | ❌ Missing | Backend endpoints not yet implemented |

## Endpoint Mappings

### Auth Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/auth/login` | ✅ | POST | User authentication |
| `/auth/register` | ✅ | POST | Register new user (admin only) |
| `/auth/refresh` | ✅ | POST | Token refresh |
| `/auth/logout` | ✅ | POST | Invalidate session |
| `/auth/me` | ✅ | GET/PATCH | Get/update current user |
| `/auth/change-password` | ✅ | POST | Change password |

### Parish Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/parishes` | ✅ | GET | List parishes (paginated) |
| `/parishes/{id}` | ✅ | GET | Get parish by ID |
| `/parishes/{id}/refresh-count` | ✅ | POST | Recalculate parcel count |

### Parcel Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/parcels` | ✅ | GET | List parcels (paginated, filterable) |
| `/parcels/{id}` | ✅ | GET/PATCH/DELETE | Parcel CRUD |
| `/parcels/by-number/{num}` | ✅ | GET | Lookup by parcel number |
| `/parcels/by-deed/{deed}` | ✅ | GET | Lookup by title deed |
| `/parcels/parish/{id}` | ✅ | GET | Parcels by parish |
| `/parcels/map` | ✅ | GET | Parcels with geometry |
| `/parcels/{id}/ownership-history` | ✅ | GET | Ownership history |

### Document Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/documents` | ✅ | GET | Search documents |
| `/documents/upload` | ✅ | POST | Upload with FormData |
| `/documents/{id}` | ✅ | GET/PATCH/DELETE | Document CRUD |
| `/documents/{id}/file` | ✅ | GET | Download file (blob) |

### GIS Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/gis/distance` | ✅ | POST | Calculate distance |
| `/gis/intersects` | ✅ | POST | Check intersection |
| `/gis/contains-point` | ✅ | POST | Point containment |
| `/gis/check-overlay` | ✅ | POST | Zoning overlay check |

### Tax Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/tax/calculate` | ✅ | POST | Tax calculation |
| `/tax/assess` | ✅ | POST | Create assessment |
| `/tax/assess/parish/{id}` | ✅ | POST | Batch assessment |
| `/tax/payments` | ✅ | POST | Record payment |
| `/tax/outstanding/{id}` | ✅ | GET | Outstanding balance |
| `/tax/history/{id}` | ✅ | GET | Payment history |
| `/tax/record/{id}` | ✅ | GET | Tax record detail |

### QR Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/qr/generate/parcel/{id}` | ✅ | POST | Generate parcel QR |
| `/qr/generate/document/{id}` | ✅ | POST | Generate document QR |
| `/qr/verify` | ✅ | POST | Verify QR code |
| `/qr/{id}` | ✅ | GET | Get QR details |
| `/qr/{id}` | ✅ | DELETE | Revoke QR code |

### Backup Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/backups` | ✅ | GET | List backup jobs |
| `/backups/trigger` | ✅ | POST | Trigger manual backup |
| `/backups/jobs/{id}` | ✅ | GET | Get job status |
| `/backups/restore` | ✅ | POST | Trigger restore |
| `/backups/restore/{id}` | ✅ | GET | Get restore status |

### Location Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/locations` | ✅ | GET | List locations |
| `/locations/{id}` | ✅ | GET/PATCH/DELETE | Location CRUD |
| `/locations/find` | ✅ | POST | Find document location |
| `/locations/cabinets` | ✅ | POST | Create cabinet |
| `/locations/cabinets/{id}` | ✅ | GET/PATCH | Cabinet CRUD |
| `/locations/{id}/grid` | ✅ | GET | Get grid layout |

### Dashboard Endpoints
| Frontend | Backend | Method | Description |
|----------|---------|--------|-------------|
| `/dashboard/stats` | ✅ | GET | System statistics |
| `/dashboard/stats/parishes` | ✅ | GET | Parish stats |
| `/dashboard/stats/parcels` | ✅ | GET | Parcel stats |
| `/dashboard/stats/users` | ✅ | GET | User stats |

## Usage Examples

### Basic API Call
```typescript
import { landService } from '@/api';

// Get all parishes
const response = await landService.getParishes();
if (response.success) {
  console.log(response.data); // Parish[]
}
```

### With React Query
```typescript
import { useQuery } from '@tanstack/react-query';
import { landService } from '@/api';

const { data, error } = useQuery({
  queryKey: ['parishes'],
  queryFn: () => landService.getParishes(),
  select: (response) => response.data
});
```

### File Upload
```typescript
import { documentService } from '@/api';

const uploadFile = async (file: File, metadata: DocumentCreate) => {
  const response = await documentService.uploadDocument(file, metadata);
  // FormData is handled automatically
};
```

### File Download
```typescript
import { documentService } from '@/api';

const downloadFile = async (id: string) => {
  const blob = await documentService.downloadDocument(id);
  // Blob can be downloaded or displayed
};
```

### Error Handling
```typescript
import { ApiError } from '@/api';

try {
  await landService.createParcel(data);
} catch (error) {
  if (error instanceof ApiError) {
    console.error(error.message); // User-friendly message
    console.error(error.errors);  // Field-specific errors
  }
}
```

## Environment Variables

Create `.env` in `land-intelligence-frontend/`:
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME="Land Intelligence"
VITE_ENABLE_DEBUG=true
```

## Vite Proxy Configuration

Add to `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
});
```

## Changes Made

1. **axios.ts**: Fixed token refresh to use `api.post()` instead of `axios.post()` for proper proxy support
2. **axios.ts**: Added `_retry` flag to prevent infinite refresh loops
3. **axios.ts**: Updated imports to use `ENDPOINTS` instead of `API_ROUTES`
4. **documentService.ts**: Fixed download to use `responseType: 'blob'`
5. **documentService.ts**: Fixed delete to pass params correctly
6. **endpoints.ts**: Updated QR and Location endpoints to match backend routes
7. **qrService.ts**: Updated to use correct endpoint paths
8. **backupService.ts**: Updated to use correct endpoint paths with params support
9. **landService.ts**: Added `getParcelsForMap()` endpoint
10. **locationService.ts**: Created new service for physical locations
11. **apiClient.ts**: Added optional config parameter for advanced use cases
12. **index.ts**: Added all missing service and type exports