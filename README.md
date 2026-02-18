# Land Intelligence & Stewardship System - Python Backend

## Overview

This is the Python FastAPI backend for the Land Intelligence & Stewardship System, a comprehensive GIS-enabled property management system designed for managing church land holdings (700+ properties).

## Features

- **GIS Analysis**: Spatial operations using PostGIS/MySQL spatial extensions
- **Document Management**: Pointer-based file system with QR code integrity
- **Tax Calculation**: Automated tax assessment with penalty engine
- **Backup System**: 3-2-1 backup strategy with local and cloud tiers
- **Physical Location Tracking**: "Find Me" feature for document retrieval
- **REST API**: Complete API for JavaFX desktop client integration

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: MySQL 8.0+ with spatial extensions
- **ORM**: SQLAlchemy 2.0 + GeoAlchemy2
- **Migrations**: Alembic
- **Validation**: Pydantic 2.5
- **GIS**: Shapely, PyProj
- **Cloud Storage**: Google Cloud Storage, Backblaze B2
- **Task Queue**: Celery (optional)

## Project Structure

```
python-backend/
├── app/                    # Application code
│   ├── api/               # REST API routes
│   ├── core/              # Core configurations
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── repositories/      # Data access layer
│   ├── utils/             # Helper utilities
│   └── tasks/             # Background tasks
├── alembic/               # Database migrations
├── config/                # YAML configurations
├── backups/               # Local backup storage
├── logs/                  # Application logs
└── tests/                 # Unit and integration tests
```

