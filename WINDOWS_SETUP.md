# Land Intelligence System - Windows 11 Setup Guide

## Quick Start for Windows 11

This guide is specifically tailored for setting up the Python backend on **Windows 11**.

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

2. **MySQL 8.0 or higher**
   - Download: https://dev.mysql.com/downloads/installer/
   - Choose "MySQL Installer for Windows"
   - Select "Developer Default" installation
   - Includes: MySQL Server, MySQL Workbench, MySQL Shell
   - Verify installation:
     ```powershell
     mysql --version
     ```

3. **Git for Windows** (optional, for version control)
   - Download: https://git-scm.com/download/win

4. **VS Code** (recommended editor)
   - Download: https://code.visualstudio.com/

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

### 5. Configure MySQL Database

**Using MySQL Workbench:**

1. Open MySQL Workbench
2. Connect to your local MySQL instance
3. Run these commands:

```sql
-- Create database
CREATE DATABASE land_intelligence_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'land_admin'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON land_intelligence_db.* TO 'land_admin'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
```

**Using Command Line:**
```powershell
# Connect to MySQL
mysql -u root -p

# Then run the SQL commands above
```

### 6. Configure Environment Variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

**Edit `.env` file** in VS Code and update these critical values:

```env
# Database password you just created
DATABASE_PASSWORD=YourSecurePassword123!

# Generate a secret key
SECRET_KEY=run_this_command_below_to_generate

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

If you see the Swagger UI documentation page, **congratulations!** ✅ Your backend is running.

---

## VS Code Configuration

### Recommended Extensions

Install these extensions in VS Code:

1. **Python** (Microsoft) - ID: ms-python.python
2. **Pylance** (Microsoft) - ID: ms-python.vscode-pylance
3. **Python Docstring Generator** - ID: njpwerner.autodocstring
4. **MySQL** (Jun Han) - ID: formulahendry.vscode-mysql

**Install all at once:**
```powershell
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension njpwerner.autodocstring
code --install-extension formulahendry.vscode-mysql
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

### MySQL Connection Issues

**Check MySQL Service:**
```powershell
# Check if MySQL is running
Get-Service MySQL80

# Start MySQL if stopped
Start-Service MySQL80
```

**Test Connection:**
```powershell
mysql -u land_admin -p -h localhost
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
   - `C:\ProgramData\MySQL`

### MySQL Performance Tuning

Edit `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`:

```ini
[mysqld]
innodb_buffer_pool_size=2G
max_connections=50
query_cache_size=0
```

Restart MySQL service after changes.

---

## Next Steps

1. ✅ Backend is running on Windows 11
2. 📱 Set up the JavaFX client application
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

# Check MySQL version
mysql --version

# List running services
Get-Service | Where-Object {$_.Status -eq "Running"}
```

---

**Setup Complete!** 🎉

Your Land Intelligence System backend is now running on Windows 11 and ready for development.
