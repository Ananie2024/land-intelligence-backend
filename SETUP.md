# Land Intelligence System - Setup Guide

## Quick Start

This guide will help you set up the **Python backend** on your development machine.

> **Database**: PostgreSQL 14+ with PostGIS extension (not MySQL)
>
> **Frontend**: React-based web UI (not JavaFX — see `land-intelligence-frontend/`)
>
> **Cache / Token blacklist**: Redis (required — `/health/ready` fails without it)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11 or higher** installed
- ✅ **PostgreSQL 14 or higher** installed and running with the **PostGIS** extension
- ✅ **Redis** installed and running (see [Redis Setup](#redis-setup) below)
- ✅ **Git** (optional, for version control)
- ✅ **Node.js 18+** and **npm** (for the React frontend; see `land-intelligence-frontend/`)
- ✅ **VS Code** or your preferred code editor

---

## Step-by-Step Setup

### 1. Extract the Project

If you received this as a ZIP file:

```bash
# Extract to your desired location
unzip land-intelligence-backend.zip
cd land-intelligence-backend
```

### 2. Verify Project Structure

Run the verification script to ensure all files are in place:

**Linux/Mac:**
```bash
python verify_structure.py
```

**Windows:**
```powershell
python verify_structure.py
```

### 3. Create Python Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required Python packages. It may take 5-10 minutes.

### 5. Configure PostgreSQL Database

**Create the database and user:**

```sql
-- Connect to PostgreSQL as the postgres superuser
psql -U postgres

-- Create the database
CREATE DATABASE land_intelligence_db;

-- Create a dedicated user
CREATE USER land_user WITH PASSWORD 'landuser11072';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE land_intelligence_db TO land_user;

-- Connect to the new database (so the schema grant takes effect)
\c land_intelligence_db

-- Grant schema-level permissions
GRANT ALL ON SCHEMA public TO land_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO land_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO land_user;

-- Enable PostGIS extension (required for GIS data)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify
\dx postgis

\q
```

> **Note**: The application uses `asyncpg` (async driver) for runtime queries and `psycopg2-binary` for synchronous operations (e.g., Alembic migrations).

### 6. Configure Environment Variables

Copy the example environment file:

**Linux/Mac:**
```bash
cp .env.example .env
```

**Windows:**
```powershell
copy .env.example .env
```

**Edit the .env file** with your settings:

Open `.env` in VS Code and update these critical values:

```env
# Database credentials (PostgreSQL, default port 5432)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=land_intelligence_db
DATABASE_USER=land_user
DATABASE_PASSWORD=landuser11072

# Generate a secret key (run this in terminal)
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=paste_generated_key_here

# Redis (required for token blacklist and Celery task queue)
REDIS_URL=redis://localhost:6379/0

# File storage paths
# Windows example:
# STORAGE_ROOT=C:/LandIntelligence
# UPLOADED_DOCUMENTS_PATH=C:/LandIntelligence/uploaded_documents

# Linux example:
STORAGE_ROOT=/home/yourusername/LandIntelligence
UPLOADED_DOCUMENTS_PATH=/home/yourusername/LandIntelligence/uploaded_documents
BACKUPS_LOCAL_PATH=/home/yourusername/LandIntelligence/backups
LOGS_PATH=/home/yourusername/LandIntelligence/logs
TEMP_PATH=/home/yourusername/LandIntelligence/temp
```

### 7. Create Required Directories

The application will auto-create directories, but you can create them manually:

**Linux/Mac:**
```bash
mkdir -p ~/LandIntelligence/{uploaded_documents,backups,logs,temp,qr-codes,gis-data}
mkdir -p ~/LandIntelligence/uploaded_documents/{land-titles,contracts,tax-records,correspondence,surveys}
mkdir -p ~/LandIntelligence/backups/{daily,weekly,monthly,manifests,temp}
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\uploaded_documents
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\backups
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\logs
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\temp
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\qr-codes
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\gis-data
```

### 8. Run Database Migrations

Initialize the database schema (this also applies the PostGIS extension check):

```bash
# Check current migration status
alembic current

# Run all migrations
alembic upgrade head
```

You should see output indicating successful migrations. If you get a PostGIS-related error,
ensure you ran `CREATE EXTENSION postgis;` on your database (see step 5).

### 9. Start the Application

**Development mode (with auto-reload):**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 10. Verify Installation

Open your browser and navigate to:

- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Documentation**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health
- **Readiness Probe** (requires Redis): http://127.0.0.1:8000/health/ready

If you see the API documentation page, congratulations! The backend is running.

---

## Redis Setup

Redis is a **hard runtime dependency** — the `/health/ready` endpoint and the
token-blacklist both fail if Redis is unavailable.

### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
# Verify
redis-cli ping
# → PONG
```

### macOS

```bash
brew install redis
brew services start redis
redis-cli ping
# → PONG
```

### Windows

Download the Microsoft archive port from:
https://github.com/microsoftarchive/redis/releases

Or install via [Memurai](https://www.memurai.com/) (a compatible Redis for Windows):

```powershell
# Using winget
winget install Memurai.Memurai

# Verify
redis-cli ping
# → PONG
```

> The default `REDIS_URL=redis://localhost:6379/0` in `.env.example` should work
> for all platforms after a standard install.

---

## React Frontend Setup

The frontend lives in the `land-intelligence-frontend/` directory within this repo.

```bash
cd land-intelligence-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The React dev server defaults to **http://localhost:5173** (Vite). The backend
CORS config already allows this origin.

See `land-intelligence-frontend/CONVENTIONS.md` for coding conventions.

---

## VS Code Setup

### Recommended Extensions

Install these VS Code extensions for the best development experience:

1. **Python** (Microsoft) — Essential Python support
2. **Pylance** (Microsoft) — Fast, feature-rich language support
3. **Python Docstring Generator** — Auto-generate docstrings
4. **autoDocstring** — Generate docstrings automatically
5. **GitLens** — Git supercharged (optional)
6. **PostgreSQL** (cweijan.vscode-postgresql-client2) — Database management

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"],
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "[python]": {
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    }
}
```

### Launch Configuration

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host",
                "127.0.0.1",
                "--port",
                "8000"
            ],
            "jinja": true,
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

---

## Cloud Backup Setup (Optional)

### Google Cloud Storage

1. Create a Google Cloud project
2. Enable Cloud Storage API
3. Create a storage bucket
4. Create a service account with "Storage Admin" role
5. Download the JSON key file
6. Update `.env`:

```env
GCS_ENABLED=True
GCS_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=your-bucket-name
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json
```

### Backblaze B2 (Alternative)

1. Create a Backblaze account
2. Create a B2 bucket
3. Generate application key
4. Update `.env`:

```env
B2_ENABLED=True
B2_ACCOUNT_ID=your_account_id
B2_APPLICATION_KEY=your_application_key
B2_BUCKET_NAME=your-bucket-name
```

---

## Troubleshooting

### "Module not found" Error

Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Database Connection Failed

Check PostgreSQL is running:
```bash
# Linux
sudo systemctl status postgresql

# Windows
Get-Service postgresql*

# Mac
brew services list
```

Verify credentials in `.env` file match your PostgreSQL setup.

**Test the connection:**
```bash
psql -U land_user -d land_intelligence_db -h localhost
```

### Redis Connection Failed

```bash
# Check if Redis is running
redis-cli ping
# Should return PONG

# If not, start it:
# Linux
sudo systemctl start redis-server

# macOS
brew services start redis

# Windows (Memurai)
net start memurai
```

### Permission Errors (Linux)

Ensure directories have correct permissions:
```bash
chmod -R 755 ~/LandIntelligence
```

### Port Already in Use

If port 8000 is occupied, change the port in `.env`:
```env
PORT=8001
```

Then run:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

---

## Running as a System Service

### Windows (using NSSM)

Download NSSM from https://nssm.cc/download

```powershell
# Install the service
nssm install LandIntelligenceAPI "C:\path\to\venv\Scripts\python.exe"
nssm set LandIntelligenceAPI AppParameters "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"
nssm set LandIntelligenceAPI AppDirectory "C:\path\to\land-intelligence-backend"
nssm set LandIntelligenceAPI Start SERVICE_AUTO_START

# Start the service
nssm start LandIntelligenceAPI

# Check status
nssm status LandIntelligenceAPI
```

### Linux (systemd)

Create `/etc/systemd/system/land-intelligence-api.service`:

```ini
[Unit]
Description=Land Intelligence FastAPI Backend
After=network.target postgresql.service redis-server.service

[Service]
Type=notify
User=yourusername
WorkingDirectory=/path/to/land-intelligence-backend
Environment="PATH=/path/to/land-intelligence-backend/venv/bin"
ExecStart=/path/to/land-intelligence-backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable land-intelligence-api
sudo systemctl start land-intelligence-api
sudo systemctl status land-intelligence-api
```

---

## Next Steps

1. ✅ Backend is running
2. 📱 Set up the React web frontend (`cd land-intelligence-frontend && npm install && npm run dev`)
3. 🗺️ Import GIS master plan data
4. 📄 Configure document templates
5. 👥 Create user accounts
6. 🧪 Test the complete workflow

---

## Getting Help

- 📖 Check the README.md for detailed documentation
- 🐛 Review logs in `logs/application.log`
- 📧 Contact IT support: it-admin@church.org

---

## Backup Testing

After setup, test the backup system:

```bash
# Trigger a manual backup
curl -X POST http://127.0.0.1:8000/api/v1/backups/trigger-manual \
  -H "Content-Type: application/json" \
  -d '{"backup_type": "FULL", "tiers": ["LOCAL"]}'

# Check backup status
curl http://127.0.0.1:8000/api/v1/backups/jobs
```

---

## Security Reminders

- ⚠️ Never commit `.env` file to version control
- ⚠️ Use strong passwords for database and application
- ⚠️ Keep cloud storage credentials secure
- ⚠️ Regularly test backup restoration
- ⚠️ Update dependencies for security patches

---

**Setup Complete!** 🎉

You're now ready to start developing the Land Intelligence System.