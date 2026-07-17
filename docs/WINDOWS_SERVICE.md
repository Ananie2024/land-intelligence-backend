# Land Intelligence System - Windows Service Deployment Guide

This guide provides comprehensive instructions for deploying the Land Intelligence API as a Windows service using NSSM (Non-Sucking Service Manager).

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [NSSM Installation](#nssm-installation)
4. [Quick Installation](#quick-installation)
5. [Manual Service Configuration](#manual-service-configuration)
6. [Service Management](#service-management)
7. [Troubleshooting](#troubleshooting)
8. [Production Checklist](#production-checklist)

---

## Overview

The Land Intelligence System is designed for single-machine Windows deployment using NSSM to manage the FastAPI backend as a Windows service. This ensures:

- Automatic startup on system boot
- Automatic restart on failure
- Proper log management
- Integration with Windows Service Control Manager
- No need for manual process management

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **PostgreSQL** | 14+ | Database (with PostGIS extension) |
| **NSSM** | 2.24+ | Windows service management |
| **Git** (optional) | Latest | Version control |

### System Requirements

- Windows 11 or Windows Server 2022
- Administrator privileges for service installation
- At least 4GB RAM (8GB recommended)
- 10GB free disk space

### PowerShell Execution Policy

If you encounter script execution errors, run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## NSSM Installation

### Step 1: Download NSSM

1. Visit: https://nssm.cc/download
2. Download the latest stable release (e.g., `nssm-2.24.zip`)
3. Extract to `C:\Program Files\NSSM\`

### Step 2: Add NSSM to PATH (Optional)

```powershell
# Run as Administrator
$env:Path += ";C:\Program Files\NSSM"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)
```

### Step 3: Verify NSSM Installation

```powershell
nssm version
# Or
"C:\Program Files\NSSM\nssm.exe" version
```

---

## Quick Installation

### Option 1: Using PowerShell (Recommended)

```powershell
# Open PowerShell as Administrator
cd C:\Projects\land-intelligence-backend\scripts

# Run the installation script
.\install-service.ps1 -Install
```

### Option 2: Using Command Prompt

```cmd
# Open Command Prompt as Administrator
cd C:\Projects\land-intelligence-backend\scripts

# Run the batch wrapper
install-service.bat -install
```

### Option 3: Validation First

```powershell
# Validate prerequisites before installation
.\test-service.ps1

# Then install if all tests pass
.\install-service.ps1 -Install
```

---

## Manual Service Configuration

If you prefer manual configuration or need to customize settings:

### Basic Installation

```powershell
# Install NSSM (as Administrator)
cd "C:\Program Files\NSSM"

# Install the service
.\nssm.exe install LandIntelligenceAPI "C:\Projects\land-intelligence-backend\venv\Scripts\python.exe"

# Configure service
.\nssm.exe set LandIntelligenceAPI AppParameters "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"
.\nssm.exe set LandIntelligenceAPI AppDirectory "C:\Projects\land-intelligence-backend"
.\nssm.exe set LandIntelligenceAPI DisplayName "Land Intelligence API"
.\nssm.exe set LandIntelligenceAPI Description "FastAPI Backend for Land Intelligence System - Digital Land Management"
.\nssm.exe set LandIntelligenceAPI Start SERVICE_AUTO_START
```

### Environment Variables

Set environment variables for the service:

```powershell
.\nssm.exe set LandIntelligenceAPI Environment "ENVIRONMENT" "production"
.\nssm.exe set LandIntelligenceAPI Environment "WORKERS" "1"
.\nssm.exe set LandIntelligenceAPI Environment "LOG_LEVEL" "INFO"
```

For full .env loading:

```powershell
# Load all variables from .env
$envContent = Get-Content "C:\Projects\land-intelligence-backend\.env"
foreach ($line in $envContent) {
    if ($line -match "^([^=]+)=(.*)$") {
        $varName = $matches[1].Trim()
        $varValue = $matches[2].Trim('"').Trim("'")
        .\nssm.exe set LandIntelligenceAPI Environment $varName $varValue
    }
}
```

### Service Recovery Configuration

Configure automatic restart behavior:

```powershell
# Restart on failure
.\nssm.exe set LandIntelligenceAPI AppRestart 1
.\nssm.exe set LandIntelligenceAPI AppRestartDelay 5000

# Set exit actions (restart on specific exit codes)
.\nssm.exe set LandIntelligenceAPI AppExit Default Exit 0
.\nssm.exe set LandIntelligenceAPI AppExit 1 Restart 5000
```

### Logging Configuration

```powershell
# Configure log output
.\nssm.exe set LandIntelligenceAPI AppStdout "C:\LandIntelligence\logs\service.log"
.\nssm.exe set LandIntelligenceAPI AppStderr "C:\LandIntelligence\logs\service.log"

# Enable file rotation (max 10MB, keep 5 backups)
.\nssm.exe set LandIntelligenceAPI AppRotateFiles "C:\LandIntelligence\logs"
.\nssm.exe set LandIntelligenceAPI AppRotateBytes 10485760
.\nssm.exe set LandIntelligenceAPI AppRotateFiles 5
```

---

## Service Management

### Start/Stop/Restart

```powershell
# Start service
.\nssm.exe start LandIntelligenceAPI

# Stop service
.\nssm.exe stop LandIntelligenceAPI

# Restart service
.\nssm.exe restart LandIntelligenceAPI
```

### Check Status

```powershell
# Using NSSM
.\nssm.exe status LandIntelligenceAPI

# Using SC (Windows built-in)
sc query LandIntelligenceAPI

# Using PowerShell
Get-Service LandIntelligenceAPI
```

### View Logs

```powershell
# View service log
Get-Content "C:\LandIntelligence\logs\service.log" -Tail 50 -Wait

# View with filtering
Get-Content "C:\LandIntelligence\logs\service.log" | Select-String "ERROR"
```

### Remove Service

```powershell
# Stop service first (if running)
.\nssm.exe stop LandIntelligenceAPI

# Remove service
.\nssm.exe remove LandIntelligenceAPI confirm
```

---

## Troubleshooting

### Service Won't Start

1. **Check service logs:**
   ```powershell
   Get-Content "C:\LandIntelligence\logs\service.log" -Tail 100
   ```

2. **Verify Python path:**
   ```powershell
   Test-Path "C:\Projects\land-intelligence-backend\venv\Scripts\python.exe"
   ```

3. **Check .env configuration:**
   ```powershell
   # Ensure critical values are set
   Select-String -Path ".env" -Pattern "SECRET_KEY", "DATABASE_PASSWORD"
   ```

4. **Verify PostgreSQL is running:**
   ```powershell
   Get-Service postgresql-x64-16
   ```

### Permission Denied Errors

```powershell
# Run as Administrator
# Right-click PowerShell -> "Run as Administrator"

# Check directory permissions
icacls "C:\LandIntelligence"
icacls "C:\Projects\land-intelligence-backend"
```

### Port Already in Use

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual PID)
taskkill /PID <PID> /F
```

### PostgreSQL Connection Issues

```powershell
# Check PostgreSQL service
Get-Service postgresql-x64-16

# Test connection
psql -h localhost -U land_user -d land_intelligence_db

# Check PostgreSQL data directory
Get-ChildItem "C:\Program Files\PostgreSQL\16\data"
```

### NSSM Not Found

```powershell
# Verify installation location
Test-Path "C:\Program Files\NSSM\nssm.exe"

# Or specify custom path
.\install-service.ps1 -Install -NssmPath "C:\custom\path\to\nssm.exe"
```

---

## Production Checklist

### Pre-Deployment

- [ ] Python 3.11+ installed and verified
- [ ] Virtual environment created and dependencies installed
- [ ] PostgreSQL 14+ installed with PostGIS extension enabled
- [ ] NSSM installed and accessible
- [ ] `.env` file configured with production values
- [ ] Required directories created (`C:\LandIntelligence\...`)
- [ ] SECRET_KEY generated and set
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Backups configured (if applicable)

### Service Configuration

- [ ] Service installed with correct Python path
- [ ] AppDirectory points to project root
- [ ] Environment variables loaded from .env
- [ ] Logging configured to `C:\LandIntelligence\logs\`
- [ ] Auto-restart enabled
- [ ] Service set to auto-start

### Security

- [ ] Windows Defender exclusions added for:
  - `C:\LandIntelligence`
  - `C:\Projects\land-intelligence-backend`
  - `C:\Program Files\PostgreSQL`
- [ ] Database user has minimal required permissions
- [ ] SECRET_KEY is cryptographically secure
- [ ] HTTPS configured (if exposed externally)

### Verification

- [ ] `test-service.ps1` passes all checks
- [ ] API accessible at `http://127.0.0.1:8000/health`
- [ ] Service starts automatically after reboot
- [ ] Logs are being written correctly
- [ ] Backup system configured (if applicable)

---

## Related Documentation

- [Windows 11 Setup Guide](../WINDOWS_SETUP.md)
- [Configuration Reference](../config/desktop_app/service_settings.yaml)
- [PostgreSQL Backup Configuration](../config/backup/)
- [API Documentation](http://127.0.0.1:8000/docs) (when running)

---

## Support

For issues or questions:
- Check logs: `C:\LandIntelligence\logs\`
- Review troubleshooting section above
- Contact: it-admin@church.org

---

**Last Updated:** 2026-07-16
**Version:** 1.0.0