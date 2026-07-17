# Land Intelligence System - Deployment Scripts

This directory contains Windows service deployment scripts for managing the Land Intelligence API as a Windows service using NSSM (Non-Sucking Service Manager).

---

## Scripts Overview

| Script | Description |
|--------|-------------|
| `install-service.ps1` | Main PowerShell script for service installation, management, and removal |
| `install-service.bat` | Command Prompt wrapper for the PowerShell script |
| `test-service.ps1` | Validation script to verify prerequisites and service configuration |

---

## Quick Start

### 1. Validate Prerequisites

Before installing the service, run the validation script to ensure all requirements are met:

```powershell
# PowerShell (as Administrator)
.\scripts\test-service.ps1
```

Expected output should show all tests passing. Fix any warnings or errors before proceeding.

### 2. Install Service

```powershell
# PowerShell (as Administrator)
.\scripts\install-service.ps1 -Install
```

Or using Command Prompt:

```cmd
# Command Prompt (as Administrator)
scripts\install-service.bat -install
```

### 3. Verify Service

After installation, verify the service is running:

```powershell
.\scripts\install-service.ps1 -Status
```

Or check the health endpoint directly:

```powershell
curl http://127.0.0.1:8000/health
```

---

## Script Usage

### install-service.ps1

```powershell
.\install-service.ps1 -<Action> [options]

Actions (choose one):
  -Install     : Install the service
  -Uninstall   : Remove the service
  -Start       : Start the service
  -Stop        : Stop the service
  -Restart     : Restart the service
  -Status      : Show service status
  -Configure   : Show current service configuration

Options:
  -ProjectPath : Path to project directory (default: C:\Projects\land-intelligence-backend)
  -ServiceName : Service name (default: LandIntelligenceAPI)
  -NssmPath    : Path to NSSM executable (default: C:\Program Files\NSSM\nssm.exe)
  -ServicePort : API port (default: 8000)
```

#### Examples

```powershell
# Install with defaults
.\install-service.ps1 -Install

# Install with custom project path
.\install-service.ps1 -Install -ProjectPath "D:\Projects\land-intelligence-backend"

# Check status
.\install-service.ps1 -Status

# Restart service
.\install-service.ps1 -Restart

# Remove service
.\install-service.ps1 -Uninstall
```

### install-service.bat

The batch file provides the same functionality for Command Prompt users:

```cmd
install-service.bat -<action> [options]

Actions:
  -install     : Install the service
  -uninstall   : Remove the service
  -start       : Start the service
  -stop        : Stop the service
  -restart     : Restart the service
  -status      : Show service status

Options:
  -project-path PATH    : Path to project directory
  -service-name NAME    : Service name
  -nssm-path PATH       : Path to NSSM executable
  -port NUMBER          : API port
  -help                 : Show help message
```

#### Examples

```cmd
install-service.bat -install
install-service.bat -status
install-service.bat -stop
```

### test-service.ps1

Validates all prerequisites and service configuration:

```powershell
.\test-service.ps1 [-Quick] [options]

Options:
  -Quick       : Skip slow checks (port tests, health checks)
  -ProjectPath : Path to project directory (default: C:\Projects\land-intelligence-backend)
  -ServiceName : Service name (default: LandIntelligenceAPI)
  -ServicePort : API port (default: 8000)
```

#### Tests Performed

| Test | Description |
|------|-------------|
| NSSM Installation | Verifies NSSM is installed and accessible |
| Python Installation | Checks Python is available in PATH |
| Virtual Environment | Validates venv exists in project directory |
| Project Structure | Ensures required files exist |
| Environment Configuration | Checks .env file and critical variables |
| PostgreSQL Service | Verifies PostgreSQL is installed and running |
| Required Directories | Checks storage directories exist |
| Python Dependencies | Validates required packages are installed |
| Service Status | Shows if service is installed/running |
| Port Availability | Checks if API port is available |
| API Health Endpoint | Verifies the API responds to health checks |

---

## Prerequisites Checklist

Before running these scripts, ensure:

### Installed Software

- [ ] **Python 3.11+** - Download from https://www.python.org/downloads/
- [ ] **PostgreSQL 14+** with PostGIS - Download from https://www.postgresql.org/download/windows/
- [ ] **NSSM 2.24+** - Download from https://nssm.cc/download

### Project Setup

- [ ] Project cloned/extracted to target directory
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example` and configured

### Directory Structure

```
C:\LandIntelligence\
├── uploaded_documents\
│   ├── land-titles\
│   ├── contracts\
│   ├── tax-records\
│   ├── correspondence\
│   └── surveys\
├── backups\
│   ├── daily\
│   ├── weekly\
│   ├── monthly\
│   └── manifests\
├── logs\
├── temp\
├── qr-codes\
│   └── generated\
└── gis-data\
    └── master-plans\
```

---

## Common Issues

### "Script must be run as Administrator"

Run PowerShell or Command Prompt as Administrator:
- Right-click on PowerShell/Command Prompt
- Select "Run as Administrator"

### "NSSM not found"

1. Download NSSM from https://nssm.cc/download
2. Extract to `C:\Program Files\NSSM\`
3. Or specify custom path: `.\install-service.ps1 -Install -NssmPath "C:\custom\nssm.exe"`

### "Python executable not found"

1. Ensure Python is installed
2. Create virtual environment: `.\venv\Scripts\python.exe -m venv venv`
3. Or specify Python path: `.\install-service.ps1 -Install -PythonPath "C:\python.exe"`

### "PostgreSQL service not running"

```powershell
# Start PostgreSQL service
Start-Service postgresql-x64-16
# Or for other versions:
Start-Service postgresql-x64-15
```

---

## Related Documentation

- [Windows Service Deployment Guide](../docs/WINDOWS_SERVICE.md)
- [Windows 11 Setup Guide](../WINDOWS_SETUP.md)
- [Service Configuration](../config/desktop_app/service_settings.yaml)

---

## Support

For issues or questions:
- Check logs: `C:\LandIntelligence\logs\service.log`
- Run validation: `.\scripts\test-service.ps1`
- Contact: it-admin@church.org