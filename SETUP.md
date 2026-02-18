# Land Intelligence System - Setup Guide

## Quick Start

This guide will help you set up the Python backend on your development machine.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11 or higher** installed
- ✅ **MySQL 8.0 or higher** installed and running
- ✅ **Git** (optional, for version control)
- ✅ **VS Code** or your preferred code editor

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

### 5. Configure MySQL Database

**Create the database:**

```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database
CREATE DATABASE land_intelligence_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'land_admin'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON land_intelligence_db.* TO 'land_admin'@'localhost';

-- Enable spatial extensions (if not already enabled)
-- MySQL 8.0+ has spatial support by default

FLUSH PRIVILEGES;
EXIT;
```

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
# Database credentials
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=land_intelligence_db
DATABASE_USER=land_admin
DATABASE_PASSWORD=your_secure_password

# Generate a secret key (run this in terminal)
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=paste_generated_key_here

# File storage paths
# Windows example:
# STORAGE_ROOT=C:/LandIntelligence
# DOCUMENTS_PATH=C:/LandIntelligence/documents

# Linux example:
STORAGE_ROOT=/home/yourusername/LandIntelligence
DOCUMENTS_PATH=/home/yourusername/LandIntelligence/documents
BACKUPS_LOCAL_PATH=/home/yourusername/LandIntelligence/backups
LOGS_PATH=/home/yourusername/LandIntelligence/logs
TEMP_PATH=/home/yourusername/LandIntelligence/temp
```

### 7. Create Required Directories

The application will auto-create directories, but you can create them manually:

**Linux/Mac:**
```bash
mkdir -p ~/LandIntelligence/{documents,backups,logs,temp,qr-codes,gis-data}
mkdir -p ~/LandIntelligence/documents/{land-titles,contracts,tax-records,correspondence,surveys}
mkdir -p ~/LandIntelligence/backups/{daily,weekly,monthly,manifests,temp}
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\documents
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\backups
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\logs
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\temp
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\qr-codes
New-Item -ItemType Directory -Force -Path C:\LandIntelligence\gis-data
```

### 8. Run Database Migrations

Initialize the database schema:

```bash
# Check current migration status
alembic current

# Run all migrations
alembic upgrade head
```

You should see output indicating successful migrations.

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

If you see the API documentation page, congratulations! The backend is running.

## VS Code Setup

### Recommended Extensions

Install these VS Code extensions for the best development experience:

1. **Python** (Microsoft) - Essential Python support
2. **Pylance** (Microsoft) - Fast, feature-rich language support
3. **Python Docstring Generator** - Auto-generate docstrings
4. **autoDocstring** - Generate docstrings automatically
5. **GitLens** - Git supercharged (optional)
6. **MySQL** (cweijan.vscode-mysql-client2) - Database management

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

## Troubleshooting

### "Module not found" Error

Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Database Connection Failed

Check MySQL is running:
```bash
# Linux
sudo systemctl status mysql

# Windows
net start MySQL80

# Mac
brew services list
```

Verify credentials in `.env` file match your MySQL setup.

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
After=network.target mysql.service

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

## Next Steps

1. ✅ Backend is running
2. 📱 Set up the JavaFX client application
3. 🗺️ Import GIS master plan data
4. 📄 Configure document templates
5. 👥 Create user accounts
6. 🧪 Test the complete workflow

## Getting Help

- 📖 Check the README.md for detailed documentation
- 🐛 Review logs in `logs/application.log`
- 📧 Contact IT support: it-admin@church.org

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

## Security Reminders

- ⚠️ Never commit `.env` file to version control
- ⚠️ Use strong passwords for database and application
- ⚠️ Keep cloud storage credentials secure
- ⚠️ Regularly test backup restoration
- ⚠️ Update dependencies for security patches

---

**Setup Complete!** 🎉

You're now ready to start developing the Land Intelligence System.
