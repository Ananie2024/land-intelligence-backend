#!/usr/bin/env sh
set -e

# =============================================================================
# Land Intelligence & Stewardship System — Hugging Face Space entrypoint
# -----------------------------------------------------------------------------
# 1. Optionally start a local redis-server (JWT token blacklist / Celery broker).
# 2. Apply Alembic migrations against the configured database (Supabase).
# 3. Serve the FastAPI app on $PORT (Hugging Face default = 7860).
# =============================================================================

echo "[entrypoint] started at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# -----------------------------------------------------------------------------
# 1) Optional local Redis (token blacklist / Celery broker)
# -----------------------------------------------------------------------------
# Token blacklist FAILS OPEN (see app/core/token_blacklist.py) when Redis is
# unavailable, so the API is fully functional without it. Set START_REDIS=true
# to run an in-memory redis inside the Space (no persistence across restarts,
# which is fine for short-lived JWT blacklist entries).
if [ "${START_REDIS:-true}" = "true" ]; then
  echo "[entrypoint] starting redis-server (in-memory)..."
  redis-server --daemonize yes --save '' --appendonly no
fi

# -----------------------------------------------------------------------------
# 2) Database migrations (Alembic)
# -----------------------------------------------------------------------------
# Runs against settings.DATABASE_URL (assembled from DATABASE_HOST/PORT/NAME/
# USER/PASSWORD). PostGIS must already be enabled on Supabase (run
# deploy/supabase/extensions.sql once via the Supabase SQL Editor).
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "[entrypoint] running database migrations (alembic upgrade head)..."
  attempts=0
  max_attempts=30
  until alembic upgrade head; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge "$max_attempts" ]; then
      echo "[entrypoint] FAILED to apply database migrations after ${max_attempts} attempts." >&2
      exit 1
    fi
    echo "[entrypoint] database not ready, retrying in 3s (${attempts}/${max_attempts})..."
    sleep 3
  done
  echo "[entrypoint] database migrations complete."
fi

# -----------------------------------------------------------------------------
# 3) Serve the API on $PORT (HF default 7860)
# -----------------------------------------------------------------------------
HOST="0.0.0.0"
PORT="${PORT:-7860}"
WORKERS="${UVICORN_WORKERS:-1}"

echo "[entrypoint] starting uvicorn on ${HOST}:${PORT} (workers=${WORKERS})..."
exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --workers "${WORKERS}"
