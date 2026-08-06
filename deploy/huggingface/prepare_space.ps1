# =============================================================================
# prepare_space.ps1 — Assemble a standalone Hugging Face Space folder
# =============================================================================
# Hugging Face Spaces deploy the ROOT of a git repo (they cannot build a
# Dockerfile nested in a subfolder). This script copies the HF Space files in
# this folder together with the backend source from the repo root into a clean
# `build/` directory that is a valid Space root, ready to be pushed as its own
# git repository / uploaded to a HF Space.
#
# Usage (from anywhere):
#   powershell -ExecutionPolicy Bypass -File deploy\huggingface\prepare_space.ps1
#
# The output goes to: deploy\huggingface\build\
# =============================================================================

[CmdletBinding()]
param(
    # Repo root (folder that contains app/, alembic/, alembic.ini, requirements.txt)
    [string]$RepoRoot,
    # Where to write the assembled Space
    [string]$OutDir
)

$ErrorActionPreference = 'Stop'

# Resolve this script's own directory robustly ($PSScriptRoot is not always
# populated, e.g. when invoked through a nested powershell -File).
if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    $hf = Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    $hf = $PSScriptRoot
}

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $hf '..\..')).Path
}
if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $hf 'build'
}

# --- clean / recreate output dir ---------------------------------------------
if (Test-Path $OutDir) { Remove-Item -Recurse -Force $OutDir }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# --- copy HF Space files ------------------------------------------------------
Copy-Item (Join-Path $hf 'Dockerfile')    $OutDir
Copy-Item (Join-Path $hf 'entrypoint.sh') $OutDir
Copy-Item (Join-Path $hf 'Spacefile')     $OutDir
Copy-Item (Join-Path $hf 'README.md')     $OutDir
Copy-Item (Join-Path $hf '.env.example')  $OutDir

# --- copy backend source from the repo root ----------------------------------
Copy-Item (Join-Path $RepoRoot 'requirements.txt') $OutDir
Copy-Item (Join-Path $RepoRoot 'alembic.ini')      $OutDir
Copy-Item (Join-Path $RepoRoot 'app')              (Join-Path $OutDir 'app')     -Recurse
Copy-Item (Join-Path $RepoRoot 'alembic')          (Join-Path $OutDir 'alembic') -Recurse

# remove Python bytecode caches from the copy
Get-ChildItem -Path $OutDir -Recurse -Directory -Filter '__pycache__' |
    Remove-Item -Recurse -Force

Write-Host ""
Write-Host "Space staged at: $OutDir" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. cd $OutDir"
Write-Host "  2. git init && git add . && git commit -m 'Hugging Face Space'"
Write-Host "  3. Push to your HF Space repo, or use the HF web UI to upload."
Write-Host "     e.g.  git remote add origin https://huggingface.co/spaces/<USER>/<SPACE>"
Write-Host ""
Write-Host "Then set the env vars (from .env.example) in the Space:"
Write-Host "  Settings -> Variables and secrets."
