# Land Intelligence System - Windows 11 Setup Guide

## Quick Start for Windows 11

This guide is specifically tailored for setting up the Python backend on **Windows 11**.

> **Database**: PostgreSQL 14+ with PostGIS extension (not MySQL)
>
> **Frontend**: React-based web UI (not JavaFX — see `land-intelligence-frontend/`)
>
> **Cache / Token blacklist**: Redis (required — `/health/ready` fails without it)

---

## Prerequisites

### Required Software

1. **Python 3.11 or higher**
   - Download: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation:
     ```powershell
     python --version
     ```

2. **PostgreSQL 14 or higher**
   - Download: https://www.postgresql.org/download/windows/
   - Choose the Windows installer from EDB
   - **Included components**: PostgreSQL Server, pgAdmin, Command Line Tools
   - **Remember the password** you set for the `postgres` superuser
   - Verify installation:
     ```powershell
     psql --version
     ```

3. **PostGIS Extension**
   - Download: https://download.osgeo.org/postgis/windows/
   - Choose the installer matching your PostgreSQL version (e.g., `postgis-bundle-pgXX-x64.zip`)
   - Or use the Stack Builder that ships with the PostgreSQL installer:
     - Start → PostgreSQL XX → Stack Builder
     - Select "PostGIS XX Bundle" from the Spatial Extensions category
   - Verify:
     ```powershell
     psql -U postgres -c "SELECT PostGIS_Version();"
     ```

4. **Redis for Windows**
   - **Option A — Memurai** (recommended, actively maintained):
     ```powershell
     winget install Memurai.Memurai
     ```
   - **Option B — Microsoft archive port**:
     Download from https://github.com/microsoftarchive/redis/releases
   - Verify:
     ```powershell
     redis-cli ping
     # → PONG
     ```

5. **Git for Windows** (optional, for version control)
   - Download: https://git-scm.com/download/win

6. **VS Code** (recommended editor)
   - Download: https://code.visualstudio.com/

7. **Node.js 18+** and **npm** (for the React frontend)
   - Download: https://nodejs.org/

---

## Step-by-Step Setup

### 1. Extract the Project

Extract `land-intelligence-backend.tar.gz` to your desired location:

**Recommended locations:**
- `C:\Projects\land-intelligence-backend`
- `C:\Users\YourUsername\Documents\land-intelligence-backend`

**Using File Explorer:**
- Right-click the `.tar.gz` file
- Extract using Windows built-in extraction or 7-Zip

**Using PowerShell:**
```powershell
# Navigate to where you want the project
cd C:\Projects

# Extract (if you have tar command available in Windows 11)
tar -xzf land-intelligence-backend.tar.gz
```

### 2. Open Project in VS Code

```powershell
cd C:\Projects\land-intelligence-backend
code .
```

### 3. Create Python Virtual Environment

**Open PowerShell in VS Code** (Terminal → New Terminal)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error:**
```powershell
# Run this once (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### 4. Install Python Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will take 5-10 minutes to download and install all packages.

### 5. Configure PostgreSQL Database

**Using pgAdmin (GUI):**

1. Open pgAdmin (installed with PostgreSQL)
2. Connect to your local PostgreSQL server (password is the one you set during PostgreSQL installation)
3. Right-click **Databases** → **Create** → **Database**
   - Name: `land_intelligence_db`
   - Owner: `postgres`
4. Open the Query Tool for your new database
5. Run these commands:

```sql
-- Create a dedicated application user
CREATE USER land_user WITH PASSWORD 'landuser11072';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE land_intelligence_db TO land_user;

-- Grant schema-level permissions
GRANT ALL ON SCHEMA public TO land_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO land_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO land_user;

-- Enable PostGIS extension (required for GIS data)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify
SELECT PostGIS_Full_Version();
```

**Using Command Line:**
```powershell
# Connect to PostgreSQL as the superuser
psql -U postgres

# Run the SQL commands from above
```

### 6. Configure Environment Variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

**Edit `.env` file** in VS Code and update these critical values:

```env
# Database credentials (PostgreSQL, default port 5432)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=land_intelligence_db
DATABASE_USER=land_user
DATABASE_PASSWORD=landuser11072

# Generate a secret key
SECRET_KEY=run_this_command_below_to_generate

# Redis (required for token blacklist and Celery task queue)
REDIS_URL=redis://localhost:6379/0

# File paths (use forward slashes!)
STORAGE_ROOT=C:/LandIntelligence
UPLOADED_DOCUMENTS_PATH=C:/LandIntelligence/uploaded_documents
BACKUPS_LOCAL_PATH=C:/LandIntelligence/backups
LOGS_PATH=C:/LandIntelligence/logs
TEMP_PATH=C:/LandIntelligence/temp
```

**Generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it in `.env` file.

### 7. Create Required Directories

**Option A: PowerShell (Recommended)**
```powershell
# Create all directories at once
$dirs = @(
    "C:\LandIntelligence\uploaded_documents\land-titles",
    "C:\LandIntelligence\uploaded_documents\contracts",
    "C:\LandIntelligence\uploaded_documents\tax-records",
    "C:\LandIntelligence\uploaded_documents\correspondence",
    "C:\LandIntelligence\uploaded_documents\surveys",
    "C:\LandIntelligence\backups\daily",
    "C:\LandIntelligence\backups\weekly",
    "C:\LandIntelligence\backups\monthly",
    "C:\LandIntelligence\backups\manifests",
    "C:\LandIntelligence\logs",
    "C:\LandIntelligence\temp",
    "C:\LandIntelligence\qr-codes\generated",
    "C:\LandIntelligence\gis-data\master-plans",
    "C:\LandIntelligence\config"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir
}

Write-Host "All directories created successfully!" -ForegroundColor Green
```

**Option B: File Explorer**
- Navigate to `C:\`
- Create folder `LandIntelligence`
- Create subfolders: `uploaded_documents`, `backups`, `logs`, `temp`, `qr-codes`, `gis-data`, `config`

### 8. Verify Project Structure

```powershell
# Make sure virtual environment is activated
python verify_structure.py
```

You should see all green checkmarks ✓

### 9. Run Database Migrations

```powershell
# Check current migration status
alembic current

# Run migrations to create tables
alembic upgrade head
```

If you get a PostGIS-related error, ensure you ran `CREATE EXTENSION postgis;` on your database (see step 5).

### 10. Start the Application

```powershell
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 11. Verify Installation

Open your web browser and navigate to:

- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health
- **Readiness Probe** (requires Redis): http://127.0.0.1:8000/health/ready

If you see the Swagger UI documentation page, **congratulations!** ✅ Your backend is running.

---

## Redis Setup for Windows

Redis is a **hard runtime dependency** — the `/health/ready` endpoint and the
token-blacklist both fail if Redis is unavailable.

### Option A: Memurai (Recommended)

[Memurai](https://www.memurai.com/) is a compatible Redis server for Windows:

```powershell
# Install via winget (Windows 10/11)
winget install Memurai.Memurai

# Memurai starts automatically as a Windows service
# Verify:
redis-cli ping
# → PONG
```

### Option B: Microsoft Archive Port

1. Download from https://github.com/microsoftarchive/redis/releases
2. Run the `.msi` installer
3. During setup, check "Add Redis to PATH"
4. Start the Redis service:
   ```powershell
   # Start Redis
   redis-server --service-start
   
   # Verify
   redis-cli ping
   # → PONG
   ```

---

## React Frontend Setup

The frontend lives in the `land-intelligence-frontend/` directory within this repo.

```powershell
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

## VS Code Configuration

### Recommended Extensions

Install these extensions in VS Code:

1. **Python** (Microsoft) — ID: ms-python.python
2. **Pylance** (Microsoft) — ID: ms-python.vscode-pylance
3. **Python Docstring Generator** — ID: njpwerner.autodocstring
4. **PostgreSQL** (Jun Han) — ID: formulahendry.vscode-postgresql

**Install all at once:**
```powershell
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension njpwerner.autodocstring
code --install-extension formulahendry.vscode-postgresql
```

### Workspace Settings

Create `.vscode\settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe",
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
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true
    }
}
```

### Debug Configuration

Create `.vscode\launch.json`:

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
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

Now you can press **F5** to start debugging!

---

## Running as Windows Service (Production)

### Using Automated Service Scripts (Recommended)

The `scripts/` directory contains automated deployment scripts for easier management:

```powershell
# Run PowerShell as Administrator
cd C:\Projects\land-intelligence-backend\scripts

# First, validate prerequisites
.\test-service.ps1

# Install the service
.\install-service.ps1 -Install

# Check service status
.\install-service.ps1 -Status
```

Or using Command Prompt:
```cmd
cd C:\Projects\land-intelligence-backend\scripts
install-service.bat -install
```

See `scripts/README.md` for detailed usage and `docs/WINDOWS_SERVICE.md` for comprehensive documentation.

### Using NSSM (Non-Sucking Service Manager) Manually

1. **Download NSSM (or use install-nssm.ps1):**
   - https://nssm.cc/download
   - Extract `nssm.exe` to `C:\Program Files\NSSM\`

2. **Install Service:**
   ```powershell
   # Run PowerShell as Administrator
   cd "C:\Program Files\NSSM"
   
   # Install the service
   .\nssm.exe install LandIntelligenceAPI "C:\Projects\land-intelligence-backend\venv\Scripts\python.exe"
   
   # Configure service
   .\nssm.exe set LandIntelligenceAPI AppParameters "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"
   .\nssm.exe set LandIntelligenceAPI AppDirectory "C:\Projects\land-intelligence-backend"
   .\nssm.exe set LandIntelligenceAPI DisplayName "Land Intelligence API"
   .\nssm.exe set LandIntelligenceAPI Description "FastAPI Backend for Land Intelligence System"
   .\nssm.exe set LandIntelligenceAPI Start SERVICE_AUTO_START
   
   # Start the service
   .\nssm.exe start LandIntelligenceAPI
   ```

3. **Manage Service:**
   ```powershell
   # Check status
   .\nssm.exe status LandIntelligenceAPI
   
   # Stop service
   .\nssm.exe stop LandIntelligenceAPI
   
   # Restart service
   .\nssm.exe restart LandIntelligenceAPI
   
   # Remove service
   .\nssm.exe remove LandIntelligenceAPI confirm
   ```

### Using Windows Task Scheduler (Alternative)

1. Open Task Scheduler
2. Create Basic Task
3. **Trigger**: At startup
4. **Action**: Start a program
   - Program: `C:\Projects\land-intelligence-backend\venv\Scripts\python.exe`
   - Arguments: `-m uvicorn app.main:app --host 127.0.0.1 --port 8000`
   - Start in: `C:\Projects\land-intelligence-backend`

---

## Cloud Backup Setup (Google Cloud Storage)

### 1. Create GCS Account

1. Go to https://console.cloud.google.com/
2. Create new project: "church-land-intelligence"
3. Enable Cloud Storage API
4. Create a storage bucket: "land-intelligence-backups"

### 2. Create Service Account

1. Go to IAM & Admin → Service Accounts
2. Create service account: "land-intelligence-backup"
3. Grant role: "Storage Admin"
4. Create JSON key
5. Download key file

### 3. Configure Application

```powershell
# Copy key file to config directory
Copy-Item "C:\Users\YourUsername\Downloads\service-account-key.json" "C:\LandIntelligence\config\"
```

Update `.env`:
```env
GCS_ENABLED=True
GCS_PROJECT_ID=church-land-intelligence
GCS_BUCKET_NAME=land-intelligence-backups
GCS_CREDENTIALS_PATH=C:/LandIntelligence/config/service-account-key.json
GCS_REGION=us-central1
```

---

## Troubleshooting

### PostgreSQL Connection Issues

**Check PostgreSQL Service:**
```powershell
# Check if PostgreSQL is running
Get-Service postgresql*

# Start PostgreSQL if stopped
Start-Service postgresql-xx  # replace xx with your version
```

**Test Connection:**
```powershell
psql -U land_user -d land_intelligence_db -h localhost
```

### Redis Connection Issues

```powershell
# Check if Redis is running
redis-cli ping
# Should return PONG

# If using Memurai:
net start memurai

# If using Microsoft Redis port:
redis-server --service-start
```

### Python Import Errors

**Ensure virtual environment is activated:**
```powershell
# You should see (venv) in prompt
# If not, activate it:
.\venv\Scripts\Activate.ps1
```

**Reinstall dependencies:**
```powershell
pip install --force-reinstall -r requirements.txt
```

### Port Already in Use

**Find what's using port 8000:**
```powershell
netstat -ano | findstr :8000
```

**Kill the process:**
```powershell
# Note the PID from previous command
taskkill /PID [PID_NUMBER] /F
```

**Or use a different port:**
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Permission Denied Errors

**Run PowerShell as Administrator:**
- Right-click PowerShell icon
- Select "Run as Administrator"

**Check directory permissions:**
```powershell
icacls C:\LandIntelligence
```

### Long Path Issues (Windows 10/11)

Enable long path support:

```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

---

## Performance Optimization (Windows)

### Windows Defender Exclusions

Add these folders to Windows Defender exclusions for better performance:

1. Open Windows Security
2. Virus & threat protection → Manage settings
3. Add exclusions:
   - `C:\LandIntelligence`
   - `C:\Projects\land-intelligence-backend`
   - `C:\ProgramData\PostgreSQL`

### PostgreSQL Performance Tuning

Edit `C:\ProgramData\PostgreSQL\XX\postgresql.conf`:

```ini
shared_buffers = 512MB          # 25% of RAM
effective_cache_size = 1.5GB    # 75% of RAM
work_mem = 64MB
maintenance_work_mem = 256MB
max_connections = 50
```

Restart PostgreSQL service after changes.

---

## Next Steps

1. ✅ Backend is running on Windows 11
2. 📱 Set up the React web frontend (`cd land-intelligence-frontend && npm install && npm run dev`)
3. 🗺️ Import GIS master plan data
4. 📄 Test document upload functionality
5. 👥 Create user accounts
6. 🧪 Run end-to-end tests

---

## Getting Help

- 📖 Check README.md for detailed documentation
- 📋 Review SETUP.md for general setup instructions
- 🐛 Check logs in `C:\LandIntelligence\logs\`
- 📧 Contact: it-admin@church.org

---

## Common Windows Commands Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Run application
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest

# Check Python version
python --version

# Check PostgreSQL version
psql --version

# Check Redis
redis-cli ping

# List running services
Get-Service | Where-Object {$_.Status -eq "Running"}
```

---

**Setup Complete!** 🎉

Your Land Intelligence System backend is now running on Windows 11 and ready for development.