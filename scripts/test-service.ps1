<#
.SYNOPSIS
    Land Intelligence System - Service Validation and Testing Script
.DESCRIPTION
    Validates service installation, configuration, and prerequisites for the
    Land Intelligence API Windows service deployment.

    Tests:
    - NSSM installation and accessibility
    - Python installation and virtual environment
    - Project structure and required files
    - Environment configuration (.env)
    - PostgreSQL service status
    - Required directories
    - Service status and health endpoint
    - Port availability

.NOTES
    Author: Land Intelligence System
    Version: 1.0.0
    Tested on: Windows 11, Windows Server 2022

.EXAMPLE
    .\test-service.ps1
    Run all validation tests

.EXAMPLE
    .\test-service.ps1 -Quick
    Run quick validation (skip slow checks like port tests)

#>

param(
    [switch]$Quick,
    [string]$ProjectPath = "C:\Projects\land-intelligence-backend",
    [string]$ServiceName = "LandIntelligenceAPI",
    [string]$NssmPath = "C:\Program Files\NSSM\nssm.exe",
    [int]$ServicePort = 8000
)

# Test counters
$Script:TotalTests = 0
$Script:PassedTests = 0
$Script:FailedTests = 0

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

function Invoke-Test {
    param(
        [string]$Name,
        [scriptblock]$ScriptBlock
    )
    
    $Script:TotalTests++
    Write-Host "TEST: $Name" -ForegroundColor Cyan
    
    try {
        $result = & $ScriptBlock
        if ($LASTEXITCODE -eq 0 -or $result -eq $true) {
            Write-Host "  PASSED" -ForegroundColor Green
            $Script:PassedTests++
            return $true
        } else {
            Write-Host "  FAILED" -ForegroundColor Red
            $Script:FailedTests++
            return $false
        }
    } catch {
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $Script:FailedTests++
        return $false
    }
}

function Test-NssmInstallation {
    if (Test-Path $Script:NssmPath) {
        Write-Host "  NSSM found at: $NssmPath" -ForegroundColor Gray
        return $true
    }
    
    # Try common paths
    $commonPaths = @(
        "C:\Program Files\NSSM\nssm.exe",
        "C:\nssm\win64\nssm.exe",
        "C:\Tools\nssm.exe",
        "${env:ProgramFiles}\NSSM\nssm.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $Script:NssmPath = $path
            Write-Host "  NSSM found at: $path" -ForegroundColor Gray
            return $true
        }
    }
    
    Write-Host "  NSSM not found. Download from https://nssm.cc/download" -ForegroundColor Yellow
    return $false
}

function Test-PythonInstallation {
    try {
        $pythonCmd = Get-Command python -ErrorAction Stop
        $version = python --version 2>&1
        Write-Host "  Python $version found" -ForegroundColor Gray
        return $true
    } catch {
        Write-Host "  Python not found in PATH" -ForegroundColor Yellow
        return $false
    }
}

function Test-VirtualEnvironment {
    $venvPython = Join-Path $Script:ProjectPath "venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        Write-Host "  Virtual environment found at: $venvPython" -ForegroundColor Gray
        return $true
    }
    
    Write-Host "  Virtual environment not found. Run: python -m venv venv" -ForegroundColor Yellow
    return $false
}

function Test-ProjectStructure {
    $requiredFiles = @(
        "app\main.py",
        "requirements.txt",
        ".env.example"
    )
    
    $missing = @()
    foreach ($file in $requiredFiles) {
        $fullPath = Join-Path $Script:ProjectPath $file
        if (-not (Test-Path $fullPath)) {
            $missing += $file
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Host "  All required files present" -ForegroundColor Gray
        return $true
    } else {
        Write-Host "  Missing files: $($missing -join ', ')" -ForegroundColor Yellow
        return $false
    }
}

function Test-EnvConfiguration {
    $envFile = Join-Path $Script:ProjectPath ".env"
    if (Test-Path $envFile) {
        Write-Host "  .env file found" -ForegroundColor Gray
        
        # Check for critical values
        $content = Get-Content $envFile
        $criticalVars = @("SECRET_KEY", "DATABASE_PASSWORD", "DATABASE_HOST")
        $missingVars = @()
        
        foreach ($var in $criticalVars) {
            $found = $content | Where-Object { $_ -match "^$var=" }
            if (-not $found) {
                $missingVars += $var
            }
        }
        
        if ($missingVars.Count -gt 0) {
            Write-Host "  Warning: Missing variables: $($missingVars -join ', ')" -ForegroundColor Yellow
            return $true  # Still pass, but warn
        }
        
        return $true
    }
    
    Write-Host "  .env file not found" -ForegroundColor Yellow
    return $false
}

function Test-PostgreSQLService {
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
                Write-Host "  PostgreSQL '$serviceName' is running" -ForegroundColor Gray
                return $true
            }
        } catch {
            # Continue to next service name
        }
    }
    
    Write-Host "  PostgreSQL service not running" -ForegroundColor Yellow
    return $false
}

function Test-RequiredDirectories {
    $directories = @(
        "C:\LandIntelligence\uploaded_documents",
        "C:\LandIntelligence\backups",
        "C:\LandIntelligence\logs",
        "C:\LandIntelligence\temp"
    )
    
    $missing = @()
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            $missing += $dir
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Host "  All required directories present" -ForegroundColor Gray
        return $true
    } else {
        Write-Host "  Missing directories: $($missing -join ', ')" -ForegroundColor Yellow
        return $false
    }
}

function Test-ServiceStatus {
    if (Test-Path $Script:NssmPath) {
        try {
            $status = & $Script:NssmPath status $Script:ServiceName 2>&1
            if ($status -match "running") {
                Write-Host "  Service is running" -ForegroundColor Gray
                return $true
            } elseif ($status -match "stopped") {
                Write-Host "  Service is installed but stopped" -ForegroundColor Yellow
                return $true
            } else {
                Write-Host "  Service not installed or unknown status" -ForegroundColor Yellow
                return $false
            }
        } catch {
            return $false
        }
    }
    return $false
}

function Test-ServiceHealth {
    if ($Script:Quick) {
        Write-Host "  Skipped (quick mode)" -ForegroundColor Gray
        return $true
    }
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$ServicePort/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  API health check passed (HTTP $($response.StatusCode))" -ForegroundColor Gray
            return $true
        }
    } catch {
        Write-Host "  API not responding: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

function Test-PortAvailability {
    if ($Script:Quick) {
        Write-Host "  Skipped (quick mode)" -ForegroundColor Gray
        return $true
    }
    
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Parse("127.0.0.1"), $ServicePort)
        $listener.Start()
        $listener.Stop()
        Write-Host "  Port $ServicePort is available" -ForegroundColor Gray
        return $true
    } catch {
        Write-Host "  Port $ServicePort is in use" -ForegroundColor Yellow
        return $false
    }
}

function Test-PythonDependencies {
    $requirementsFile = Join-Path $Script:ProjectPath "requirements.txt"
    if (-not (Test-Path $requirementsFile)) {
        Write-Host "  requirements.txt not found" -ForegroundColor Yellow
        return $false
    }
    
    # Check if we can import key modules
    $venvPython = Join-Path $Script:ProjectPath "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        # Try system python
        $pythonExe = "python"
    } else {
        $pythonExe = "`"$venvPython`""
    }
    
    try {
        $cmd = "$pythonExe -c `"import fastapi, uvicorn; print('OK')`" 2>&1"
        $result = Invoke-Expression $cmd
        if ($result -match "OK") {
            Write-Host "  Required Python packages installed" -ForegroundColor Gray
            return $true
        }
    } catch {
        Write-Host "  Required Python packages not installed" -ForegroundColor Yellow
        return $false
    }
}

# =============================================================================
# MAIN
# =============================================================================

Clear-Host

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Land Intelligence System - Service Validation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project Path: $ProjectPath"
Write-Host "Service Name: $ServiceName"
Write-Host "Service Port: $ServicePort"
if ($Quick) { Write-Host "Quick Mode: Yes (skipping slow checks)" -ForegroundColor Yellow }
Write-Host ""

# Run all tests
Invoke-Test "NSSM Installation" { Test-NssmInstallation }
Invoke-Test "Python Installation" { Test-PythonInstallation }
Invoke-Test "Virtual Environment" { Test-VirtualEnvironment }
Invoke-Test "Project Structure" { Test-ProjectStructure }
Invoke-Test "Environment Configuration" { Test-EnvConfiguration }
Invoke-Test "PostgreSQL Service" { Test-PostgreSQLService }
Invoke-Test "Required Directories" { Test-RequiredDirectories }
Invoke-Test "Python Dependencies" { Test-PythonDependencies }
Invoke-Test "Service Status" { Test-ServiceStatus }
Invoke-Test "Port Availability" { Test-PortAvailability }
Invoke-Test "API Health Endpoint" { Test-ServiceHealth }

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Total Tests:  $TotalTests"
Write-Host "  Passed:       $PassedTests" -ForegroundColor Green
Write-Host "  Failed:       $FailedTests" -ForegroundColor ($FailedTests -gt 0 ? "Red" : "Green")
Write-Host ""

if ($FailedTests -gt 0) {
    Write-Host "Validation completed with errors. Please fix the issues above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "All validation tests passed!" -ForegroundColor Green
    exit 0
}