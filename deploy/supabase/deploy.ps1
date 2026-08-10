# =============================================================================
# deploy/supabase/deploy.ps1 — Deploy the Land Intelligence DB to Supabase
# =============================================================================
# Helper that:
#   1. Loads Supabase connection settings (env vars, or a local .env.supabase).
#   2. Applies extensions.sql (PostGIS) via psql (skipped when SQL_EDITOR_ONLY=1).
#   3. Verifies PostGIS.
#   4. Runs `alembic upgrade head` against the Supabase database.
#
# Usage (from the repo root):
#   powershell -ExecutionPolicy Bypass -File deploy/supabase/deploy.ps1
#
# It reads these variables (from the environment or a .env.supabase file in this
# folder). Get the real values from:
#   Supabase Dashboard -> Project jbaohbvvjsfmhmvlsufb
#   -> Project Settings -> Database -> Connection string (Session pooler).
#
#   DATABASE_HOST       e.g. aws-0-<REGION>.pooler.supabase.com
#   DATABASE_PORT       e.g. 5432  (session pooler)
#   DATABASE_NAME       e.g. postgres
#   DATABASE_USER       e.g. postgres.jbaohbvvjsfmhmvlsufb
#   DATABASE_PASSWORD   <database password> (NOT the account login password)
#   SECRET_KEY          any random >=32 char string (required by Settings)
# =============================================================================
$ErrorActionPreference = "Stop"
$ROOT = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $ROOT

# -----------------------------------------------------------------------------
# 1) Load settings: prefer a local .env.supabase, else current environment.
# -----------------------------------------------------------------------------
$envFile = Join-Path $PSScriptRoot ".env.supabase"
if (Test-Path $envFile) {
    Write-Host "Loading connection settings from $envFile"
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([A-Z0-9_]+)\s*=\s*"?([^"#]*)"?\s*(#.*)?$') {
            Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2]
        }
    }
}

function Get-Req([string]$name) {
    $v = [System.Environment]::GetEnvironmentVariable($name)
    if ([string]::IsNullOrWhiteSpace($v)) {
        throw "Missing required variable: $name (set it in .env.supabase or the environment)."
    }
    return $v
}

$HOST_    = Get-Req "DATABASE_HOST"
$PORT_    = Get-Req "DATABASE_PORT"
$NAME_    = Get-Req "DATABASE_NAME"
$USER_    = Get-Req "DATABASE_USER"
$PASSWORD_= Get-Req "DATABASE_PASSWORD"
$SECRET_  = Get-Req "SECRET_KEY"

# Universal password: needed by psql and by SQLAlchemy URL.
$env:PGPASSWORD = $PASSWORD_

# -----------------------------------------------------------------------------
# 2) Apply extensions.sql (PostGIS) unless SQL_EDITOR_ONLY=1 (user runs it in
#    the Supabase SQL Editor, which is the recommended one-time step).
# -----------------------------------------------------------------------------
$SQL_EDITOR_ONLY = [System.Environment]::GetEnvironmentVariable("SQL_EDITOR_ONLY")
if ($SQL_EDITOR_ONLY -ne "1") {
    $psql = "psql"
    Write-Host "Applying deploy/supabase/extensions.sql (PostGIS) via psql..."
    & $psql -h $HOST_ -p $PORT_ -U $USER_ -d $NAME_ -v ON_ERROR_STOP=1 `
        -f (Join-Path $PSScriptRoot "extensions.sql")
    if ($LASTEXITCODE -ne 0) { throw "psql failed applying extensions.sql (exit $LASTEXITCODE)" }
    Write-Host "PostGIS extension applied."
} else {
    Write-Host "SQL_EDITOR_ONLY=1 -> please run deploy/supabase/extensions.sql in the Supabase SQL Editor."
}

# -----------------------------------------------------------------------------
# 3) Build the schema from the app models and stamp Alembic at head.
#    (bootstrap_schema.py replaces `alembic upgrade head`: the migration history
#    is not runnable from an empty database — see deploy/supabase/README.md.)
# -----------------------------------------------------------------------------
Write-Host "Deploying schema to $HOST_/$NAME_ (bootstrap from models + stamp head)..."
$env:DATABASE_HOST     = $HOST_
$env:DATABASE_PORT     = $PORT_
$env:DATABASE_NAME     = $NAME_
$env:DATABASE_USER     = $USER_
$env:DATABASE_PASSWORD = $PASSWORD_
$env:SECRET_KEY        = $SECRET_

& .\venv\Scripts\python.exe (Join-Path $PSScriptRoot "bootstrap_schema.py")
if ($LASTEXITCODE -ne 0) { throw "bootstrap_schema.py failed (exit $LASTEXITCODE)" }

Write-Host "Current migration version:"
& .\venv\Scripts\python.exe -m alembic current

Write-Host "`nDatabase deployment to Supabase ($HOST_/$NAME_) complete."
Pop-Location
