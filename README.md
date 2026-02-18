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

## Installation

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- pip or Poetry package manager

### Setup Steps

1. **Clone the repository** (or extract the archive)

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # OR using Poetry
   poetry install
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

5. **Create MySQL database**:
   ```sql
   CREATE DATABASE land_intelligence_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'land_admin'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON land_intelligence_db.* TO 'land_admin'@'localhost';
   FLUSH PRIVILEGES;
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Create required directories**:
   ```bash
   # The application will auto-create these, but you can create manually:
   mkdir -p ~/LandIntelligence/{documents,backups,logs,temp,qr-codes,gis-data}
   ```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### As Windows Service (using NSSM)

```powershell
nssm install LandIntelligenceAPI "C:\path\to\venv\Scripts\python.exe" "C:\path\to\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000"
nssm start LandIntelligenceAPI
```

### As Linux systemd Service

Create `/etc/systemd/system/land-intelligence-api.service`:

```ini
[Unit]
Description=Land Intelligence FastAPI Service
After=network.target mysql.service

[Service]
Type=notify
User=your_user
WorkingDirectory=/path/to/python-backend
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable land-intelligence-api
sudo systemctl start land-intelligence-api
```

## API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## Backup Configuration

### Cloud Backup Setup (Google Cloud Storage)

1. Create a GCS bucket in your Google Cloud project
2. Create a service account with Storage Admin role
3. Download the service account JSON key
4. Update `.env` with:
   ```
   GCS_ENABLED=True
   GCS_PROJECT_ID=your-project-id
   GCS_BUCKET_NAME=your-bucket-name
   GCS_CREDENTIALS_PATH=/path/to/service-account-key.json
   ```

### Backup Schedules

Edit `config/backup/backup_schedule.yaml` to customize backup schedules.

Default schedules:
- **Daily incremental**: 3:00 AM
- **Weekly full**: Sunday 2:00 AM
- **Monthly archive**: 1st of month 2:00 AM

### Manual Backup Trigger

```bash
curl -X POST http://127.0.0.1:8000/api/v1/backups/trigger-manual \
  -H "Content-Type: application/json" \
  -d '{"backup_type": "FULL", "tiers": ["LOCAL", "CLOUD"]}'
```

## Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=app --cov-report=html
```

### Run specific test file

```bash
pytest tests/unit/test_gis_services.py
```

## Development Guidelines

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **mypy** for type checking

Format code:
```bash
black app/
isort app/
flake8 app/
mypy app/
```

### Architectural Principles

1. **ORM-First**: No raw SQL queries; use SQLAlchemy
2. **Repository Pattern**: All database access through repositories
3. **Service Layer**: Business logic in service classes
4. **Pydantic Validation**: All input/output validated with schemas
5. **Dependency Injection**: Use FastAPI's dependency system

## Troubleshooting

### Database Connection Issues

Check MySQL is running:
```bash
# Linux
sudo systemctl status mysql

# Windows
net start MySQL80
```

Verify credentials in `.env` file.

### Import Errors

Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Backup Failures

Check logs in `logs/backup.log`:
```bash
tail -f logs/backup.log
```

Verify cloud credentials and network connectivity.

## Production Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure cloud backup credentials
- [ ] Set up automated backup schedules
- [ ] Configure email notifications
- [ ] Enable HTTPS (if exposing beyond localhost)
- [ ] Set up log rotation
- [ ] Test disaster recovery procedure
- [ ] Document restore process
- [ ] Train staff on system usage

## License

Proprietary - Church Internal Use Only

## Support

For technical support, contact:
- IT Administrator: it-admin@church.org
- System Issues: support@church.org

## Version History

- **1.0.0** (2025-02-04): Initial release
  - Core GIS functionality
  - Document management with QR codes
  - Tax calculation engine
  - 3-2-1 backup system
  - Desktop single-machine deployment
