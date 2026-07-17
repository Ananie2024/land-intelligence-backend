<#
.SYNOPSIS
    Land Intelligence System - NSSM Installation Helper
.DESCRIPTION
    Downloads and installs NSSM (Non-Sucking Service Manager) if not already present.
    This script automates the NSSM setup process.

.NOTES
    Author: Land Intelligence System
    Version: 1.0.0
    Tested on: Windows 11, Windows Server 2022

.EXAMPLE
    .\install-nssm.ps1
    Downloads and installs NSSM to the default location

.EXAMPLE
    .\install-nssm.ps1 -InstallPath "C:\Custom\NSSM"
    Installs NSSM to a custom location

#>

param(
    [string]$InstallPath = "C:\Program Files\NSSM",
    [string]$TempPath = "$env:TEMP\nssm-install"
)

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

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor White
}

# Check for admin privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Error-Custom "This script must be run as Administrator!"
    Write-Info "Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

Write-Header "NSSM Installation Helper"

# Check if NSSM already exists
$nssmExe = Join-Path $InstallPath "nssm.exe"
if (Test-Path $nssmExe) {
    Write-Success "NSSM already installed at: $nssmExe"
    & $nssmExe version
    exit 0
}

Write-Info "Downloading NSSM..."

# Create temp directory
if (-not (Test-Path $TempPath)) {
    New-Item -ItemType Directory -Force -Path $TempPath | Out-Null
}

# Determine system architecture
if ([Environment]::Is64BitOperatingSystem) {
    $arch = "win64"
} else {
    $arch = "win32"
}

# Download URL for NSSM
$nssmVersion = "2.24"
$nssmUrl = "https://nssm.cc/release/nssm-$nssmVersion.zip"
$zipPath = Join-Path $TempPath "nssm.zip"

try {
    # Download NSSM
    Write-Info "Downloading from: $nssmUrl"
    Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath -UseBasicParsing
    
    if (-not (Test-Path $zipPath)) {
        Write-Error-Custom "Failed to download NSSM"
        exit 1
    }
    
    # Extract ZIP
    Write-Info "Extracting NSSM..."
    Expand-Archive -Path $zipPath -DestinationPath $TempPath -Force
    
    # Find extracted nssm.exe
    $extractedNssm = Get-ChildItem -Path $TempPath -Recurse -Filter "nssm.exe" | Select-Object -First 1
    if (-not $extractedNssm) {
        Write-Error-Custom "Could not find nssm.exe in extracted archive"
        exit 1
    }
    
    # Create install directory
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
    
    # Copy nssm.exe
    Copy-Item $extractedNssm.FullName $nssmExe -Force
    Write-Success "NSSM installed to: $InstallPath"
    
    # Clean up
    Remove-Item $TempPath -Recurse -Force
    
    # Verify installation
    & $nssmExe version
    
    Write-Host ""
    Write-Info "To add NSSM to PATH, run:"
    Write-Host "  `$env:Path += \";$InstallPath\`"\n[Environment]::SetEnvironmentVariable(\"Path\", `$env:Path, [EnvironmentVariableTarget]::Machine)" -ForegroundColor Yellow
    
} catch {
    Write-Error-Custom "Installation failed: $($_.Exception.Message)"
    
    # Manual installation instructions
    Write-Host ""
    Write-Info "Manual installation:"
    Write-Host "  1. Download from: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "  2. Extract nssm-$nssmVersion.zip" -ForegroundColor Yellow
    Write-Host "  3. Copy $arch\nssm.exe to $InstallPath" -ForegroundColor Yellow
    
    exit 1
}