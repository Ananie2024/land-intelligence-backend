<#
.SYNOPSIS
    Land Intelligence System - Windows Service Installation Script (NSSM)
.DESCRIPTION
    Installs the Land Intelligence API as a Windows service using NSSM (Non-Sucking Service Manager).
    This script handles service registration, configuration, and startup for production deployment.

    Prerequisites:
    - Python 3.11+ installed and added to PATH
    - NSSM (Non-Sucking Service Manager) installed
    - PostgreSQL service running (postgresql-x64-16 or similar)
    - Virtual environment created in the project directory
    - .env configuration file present and configured

.NOTES
    Author: Land Intelligence System
    Version: 1.0.0
    Tested on: Windows 11, Windows Server 2022
    PowerShell Version: 5.1+

.EXAMPLE
    .\install-service.ps1 -Install
    Installs the Land Intelligence API service

.EXAMPLE
    .\install-service.ps1 -Uninstall
    Removes the Land Intelligence API service

.EXAMPLE
    .\install-service.ps1 -Start
    Starts the Land Intelligence API service

.EXAMPLE
    .\install-service.ps1 -Status
    Shows the current status of the service

#>

param(
    [Parameter(ParameterSetName="Install")]
    [switch]$Install,

    [Parameter(ParameterSetName="Uninstall")]
    [switch]$Uninstall,

    [Parameter(ParameterSetName="Start")]
    [switch]$Start,

    [Parameter(ParameterSetName="Stop")]
    [switch]$Stop,

    [Parameter(ParameterSetName="Restart")]
    [switch]$Restart,

    [Parameter(ParameterSetName="Status")]
    [switch]$Status,

    [Parameter(ParameterSetName="Configure")]
    [switch]$Configure,

    [string]$ProjectPath = "C:\Projects\land-intelligence-backend",
    [string]$ServiceName = "LandIntelligenceAPI",
    [string]$NssmPath = "C:\Program Files\NSSM\nssm.exe",
    [string]$PythonPath = $null,
    [int]$ServicePort = 8000
)

# Requires Administrator privileges
$Script:RequiresAdmin = $true

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor White
}

function Test-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Nssm {
    if (Test-Path $Script:NssmPath) {
        return $true
    }
    
    # Try to find NSSM in PATH or common locations
    $commonPaths = @(
        "C:\Program Files\NSSM\nssm.exe",
        "C:\nssm\win64\nssm.exe",
        "C:\Tools\nssm.exe",
        "${env:ProgramFiles}\NSSM\nssm.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $Script:NssmPath = $path
            return $true
        }
    }
    
    return $false
}

function Get-PythonPath {
    if ($Script:PythonPath) {
        return $Script:PythonPath
    }
    
    # Look for virtual environment python
    $venvPython = Join-Path $Script:ProjectPath "venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }
    
    # Fall back to system Python
    try {
        $pythonCmd = Get-Command python -ErrorAction Stop
        return $pythonCmd.Source
    } catch {
        return $null
    }
}

function Test-PostgreSQL {
    $pgServiceNames = @(
        "postgresql-x64-16",
        "postgresql-x64-15",
        "postgresql-x64-14",
        "postgresql-x64-13",
        "postgresql",
        "PostgreSQL"
    )
    
    foreach ($serviceName in $pgServiceNames) {
        try {
            $service = Get-Service -Name $serviceName -ErrorAction Stop
            if ($service.Status -eq "Running") {
                return @{
                    Found = $true
                    Name = $serviceName
                    Status = $service.Status
                }
            }
        } catch {
            # Service not found, try next
        }
    }
    
    return @{ Found = $false; Name = $null; Status = $null }
}

function Initialize-Directories {
    $directories = @(
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
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
            Write-Info "Created directory: $dir"
        }
    }
}

function Import-ServiceSettings {
    $settingsFile = Join-Path $Script:ProjectPath "config\desktop_app\service_settings.yaml"
    
    if (Test-Path $settingsFile) {
        try {
            # Simple YAML parsing for the settings we need
            $content = Get-Content $settingsFile
            $settings = @{}
            
            foreach ($line in $content) {
                if ($line -match "^\s+(\w+):\s*(.+)$") {
                    $key = $matches[1]
                    $value = $matches[2].Trim('"')
                    $settings[$key] = $value
                }
            }
            
            return $settings
        } catch {
            Write-Warning-Custom "Could not parse service settings file, using defaults"
            return $null
        }
    }
    
    return $null
}

# =============================================================================
# SERVICE MANAGEMENT FUNCTIONS
# =============================================================================

function Install-Service {
    Write-Header "Installing Land Intelligence API Service"
    
    # Verify admin privileges
    if (-not (Test-Admin)) {
        Write-Error-Custom "This script must be run as Administrator!"
        Write-Info "Right-click PowerShell and select 'Run as Administrator'"
        exit 1
    }
    
    # Check prerequisites
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $NssmPath"
        Write-Info "Download NSSM from: https://nssm.cc/download"
        Write-Info "Extract to: C:\Program Files\NSSM\"
        exit 1
    }
    Write-Success "NSSM found at: $Script:NssmPath"
    
    # Check Python
    $pythonPath = Get-PythonPath
    if (-not $pythonPath) {
        Write-Error-Custom "Python executable not found!"
        Write-Info "Please create a virtual environment or ensure Python is in PATH"
        exit 1
    }
    Write-Success "Python found at: $pythonPath"
    
    # Check project path
    if (-not (Test-Path $Script:ProjectPath)) {
        Write-Error-Custom "Project path does not exist: $Script:ProjectPath"
        Write-Info "Please clone or extract the project first"
        exit 1
    }
    
    # Check if .env exists
    $envFile = Join-Path $Script:ProjectPath ".env"
    if (-not (Test-Path $envFile)) {
        Write-Warning-Custom ".env file not found. Creating from .env.example..."
        $envExample = Join-Path $Script:ProjectPath ".env.example"
        if (Test-Path $envExample) {
            Copy-Item $envExample $envFile
            Write-Info "Please edit .env with your actual configuration values"
        } else {
            Write-Error-Custom ".env.example not found. Please create .env manually"
            exit 1
        }
    }
    
    # Check PostgreSQL
    $pgStatus = Test-PostgreSQL
    if (-not $pgStatus.Found) {
        Write-Warning-Custom "PostgreSQL service not running. Please ensure it's installed and started."
    } else {
        Write-Success "PostgreSQL service '$($pgStatus.Name)' is $($pgStatus.Status)"
    }
    
    # Create required directories
    Initialize-Directories
    
    # Import service settings
    $settings = Import-ServiceSettings
    
    # Build NSSM install command
    $appPath = $pythonPath
    $appArgs = "-m uvicorn app.main:app --host 127.0.0.1 --port $ServicePort"
    $appDir = $Script:ProjectPath
    
    Write-Info "Installing service with the following configuration:"
    Write-Info "  Service Name: $ServiceName"
    Write-Info "  Python Path: $appPath"
    Write-Info "  Arguments: $appArgs"
    Write-Info "  Working Directory: $appDir"
    
    # Install service using NSSM
    try {
        & $Script:NssmPath install $ServiceName $appPath $appArgs 2>&1 | Out-Null
        
        # Configure service parameters
        & $Script:NssmPath set $ServiceName AppDirectory $appDir | Out-Null
        & $Script:NssmPath set $ServiceName DisplayName "Land Intelligence API" | Out-Null
        & $Script:NssmPath set $ServiceName Description "FastAPI Backend for Land Intelligence System - Digital Land Management" | Out-Null
        & $Script:NssmPath set $ServiceName Start SERVICE_AUTO_START | Out-Null
        & $Script:NssmPath set $ServiceName AppRestartDelay 5000 | Out-Null
        & $Script:NssmPath set $ServiceName AppRestart 1 | Out-Null
        & $Script:NssmPath set $ServiceName AppExit Default Exit 0 | Out-Null
        
        # Set environment variables for the service
        $envPath = Join-Path $Script:ProjectPath ".env"
        if (Test-Path $envPath) {
            $envContent = Get-Content $envPath
            $envVars = @{}
            foreach ($line in $envContent) {
                if ($line -match "^([^=]+)=(.*)$") {
                    $varName = $matches[1].Trim()
                    $varValue = $matches[2].Trim('"').Trim("'")
                    $envVars[$varName] = $varValue
                }
            }
            
            # Add PATH to include venv Scripts if available
            $venvScripts = Join-Path $Script:ProjectPath "venv\Scripts"
            if (Test-Path $venvScripts) {
                $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
                $envVars["PATH"] = "$venvScripts;$currentPath"
            }
            
            foreach ($key in $envVars.Keys) {
                & $Script:NssmPath set $ServiceName Environment $key $envVars[$key] | Out-Null
            }
        }
        
        # Set log output (optional but recommended)
        $logPath = "C:\LandIntelligence\logs\service.log"
        & $Script:NssmPath set $ServiceName AppStdout $logPath | Out-Null
        & $Script:NssmPath set $ServiceName AppStderr $logPath | Out-Null
        
        Write-Success "Service '$ServiceName' installed successfully!"
        
    } catch {
        Write-Error-Custom "Failed to install service: $($_.Exception.Message)"
        exit 1
    }
    
    # Ask to start service
    $startNow = Read-Host "Start the service now? (Y/N)"
    if ($startNow -eq "Y" -or $startNow -eq "y") {
        Start-Service-Now
    }
}

function Uninstall-Service {
    Write-Header "Uninstalling Land Intelligence API Service"
    
    if (-not (Test-Admin)) {
        Write-Error-Custom "This script must be run as Administrator!"
        exit 1
    }
    
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $Script:NssmPath"
        exit 1
    }
    
    # Check if service exists
    $serviceExists = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if (-not $serviceExists) {
        Write-Warning-Custom "Service '$ServiceName' does not exist"
        exit 0
    }
    
    # Stop service if running
    try {
        $status = & $Script:NssmPath status $ServiceName 2>&1
        if ($status -match "running") {
            Write-Info "Stopping service..."
            & $Script:NssmPath stop $ServiceName | Out-Null
            Start-Sleep -Seconds 2
        }
    } catch {
        # Service might not be running
    }
    
    # Remove service
    try {
        & $Script:NssmPath remove $ServiceName confirm | Out-Null
        Write-Success "Service '$ServiceName' removed successfully!"
    } catch {
        Write-Error-Custom "Failed to remove service: $($_.Exception.Message)"
        exit 1
    }
}

function Start-Service-Now {
    Write-Header "Starting Land Intelligence API Service"
    
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $Script:NssmPath"
        exit 1
    }
    
    # Wait for PostgreSQL
    $waitForDb = Read-Host "Wait for PostgreSQL to be ready? (Y/N)"
    if ($waitForDb -eq "Y" -or $waitForDb -eq "y") {
        Write-Info "Waiting for PostgreSQL service..."
        $timeout = 30
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            $pgStatus = Test-PostgreSQL
            if ($pgStatus.Found) {
                Write-Success "PostgreSQL is running"
                break
            }
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
        
        if ($elapsed -ge $timeout) {
            Write-Warning-Custom "PostgreSQL not detected within timeout. Starting anyway..."
        }
    }
    
    try {
        & $Script:NssmPath start $ServiceName | Out-Null
        Start-Sleep -Seconds 3
        
        $status = & $Script:NssmPath status $ServiceName 2>&1
        if ($status -match "running") {
            Write-Success "Service started successfully!"
            Write-Info "API available at: http://127.0.0.1:$ServicePort"
            Write-Info "API Documentation: http://127.0.0.1:$ServicePort/docs"
        } else {
            Write-Error-Custom "Service failed to start. Check logs at: C:\LandIntelligence\logs\service.log"
        }
    } catch {
        Write-Error-Custom "Failed to start service: $($_.Exception.Message)"
        exit 1
    }
}

function Stop-Service-Now {
    Write-Header "Stopping Land Intelligence API Service"
    
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $Script:NssmPath"
        exit 1
    }
    
    try {
        & $Script:NssmPath stop $ServiceName | Out-Null
        Write-Success "Service stopped successfully!"
    } catch {
        Write-Error-Custom "Failed to stop service: $($_.Exception.Message)"
        exit 1
    }
}

function Restart-Service-Now {
    Write-Header "Restarting Land Intelligence API Service"
    
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $Script:NssmPath"
        exit 1
    }
    
    try {
        & $Script:NssmPath restart $ServiceName | Out-Null
        Start-Sleep -Seconds 3
        
        $status = & $Script:NssmPath status $ServiceName 2>&1
        if ($status -match "running") {
            Write-Success "Service restarted successfully!"
        } else {
            Write-Warning-Custom "Service may not have started. Check status manually."
        }
    } catch {
        Write-Error-Custom "Failed to restart service: $($_.Exception.Message)"
        exit 1
    }
}

function Get-ServiceStatus {
    Write-Header "Land Intelligence API Service Status"
    
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $Script:NssmPath"
        exit 1
    }
    
    try {
        $status = & $Script:NssmPath status $ServiceName 2>&1
        Write-Info "Service Status: $status"
        
        # Also check Windows service status
        try {
            $winService = Get-Service -Name $ServiceName -ErrorAction Stop
            Write-Info "Windows Service Status: $($winService.Status)"
            Write-Info "Windows Service Name: $($winService.Name)"
            Write-Info "Display Name: $($winService.DisplayName)"
        } catch {
            Write-Warning-Custom "Windows service not found in Service Control Manager"
        }
        
        # Check if API is responding
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$ServicePort/health" -UseBasicParsing -ErrorAction Stop
            Write-Success "API Health Check: $($response.StatusCode)"
        } catch {
            Write-Warning-Custom "API not responding on port $ServicePort"
        }
        
        # Check PostgreSQL
        $pgStatus = Test-PostgreSQL
        if ($pgStatus.Found) {
            Write-Success "PostgreSQL ('$($pgStatus.Name)'): $($pgStatus.Status)"
        } else {
            Write-Warning-Custom "PostgreSQL: Not detected or not running"
        }
        
    } catch {
        Write-Error-Custom "Failed to get service status: $($_.Exception.Message)"
        exit 1
    }
}

function Configure-Service {
    Write-Header "Configuring Land Intelligence API Service"
    
    if (-not (Test-Admin)) {
        Write-Error-Custom "This script must be run as Administrator!"
        exit 1
    }
    
    if (-not (Test-Nssm)) {
        Write-Error-Custom "NSSM not found at: $Script:NssmPath"
        exit 1
    }
    
    # Check if service exists
    $serviceExists = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if (-not $serviceExists) {
        Write-Error-Custom "Service '$ServiceName' does not exist. Install it first."
        exit 1
    }
    
    Write-Info "Current service configuration:"
    & $Script:NssmPath get $ServiceName 2>&1 | ForEach-Object { Write-Info "  $_" }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

Write-Header "Land Intelligence System - Service Management"

# Determine action
$actions = @()
if ($Install) { $actions += "Install" }
if ($Uninstall) { $actions += "Uninstall" }
if ($Start) { $actions += "Start" }
if ($Stop) { $actions += "Stop" }
if ($Restart) { $actions += "Restart" }
if ($Status) { $actions += "Status" }
if ($Configure) { $actions += "Configure" }

if ($actions.Count -eq 0) {
    Write-Info "Usage: .\install-service.ps1 -<Action>"
    Write-Host ""
    Write-Host "Available actions:" -ForegroundColor White
    Write-Host "  -Install     : Install the service" -ForegroundColor White
    Write-Host "  -Uninstall   : Remove the service" -ForegroundColor White
    Write-Host "  -Start       : Start the service" -ForegroundColor White
    Write-Host "  -Stop        : Stop the service" -ForegroundColor White
    Write-Host "  -Restart     : Restart the service" -ForegroundColor White
    Write-Host "  -Status      : Show service status" -ForegroundColor White
    Write-Host "  -Configure   : Show/update service configuration" -ForegroundColor White
    Write-Host ""
    Write-Host "Optional parameters:" -ForegroundColor White
    Write-Host "  -ProjectPath : Path to project directory (default: C:\Projects\land-intelligence-backend)" -ForegroundColor White
    Write-Host "  -ServiceName : Service name (default: LandIntelligenceAPI)" -ForegroundColor White
    Write-Host "  -NssmPath    : Path to NSSM executable (default: C:\Program Files\NSSM\nssm.exe)" -ForegroundColor White
    Write-Host "  -ServicePort : API port (default: 8000)" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\install-service.ps1 -Install" -ForegroundColor White
    Write-Host "  .\install-service.ps1 -Status" -ForegroundColor White
    exit 0
}

# Execute requested action
foreach ($action in $actions) {
    switch ($action) {
        "Install" { Install-Service }
        "Uninstall" { Uninstall-Service }
        "Start" { Start-Service-Now }
        "Stop" { Stop-Service-Now }
        "Restart" { Restart-Service-Now }
        "Status" { Get-ServiceStatus }
        "Configure" { Configure-Service }
    }
}

Write-Header "Operation Complete"
Write-Success "Done!"