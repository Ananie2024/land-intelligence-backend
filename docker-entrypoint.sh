#!/usr/bin/env sh
set -e

# =============================================================================
# Land Intelligence & Stewardship System - Backend entrypoint
# -----------------------------------------------------------------------------
# Runs before whatever role this container launches (API, Celery worker, Celery
# beat) so the schema is up to date before the process starts talking to the DB.
#
# docker-compose's `db` service is brand-new Postgres on first boot (and any
# hosted/managed database starts empty too), so without migrations here the app
# would boot against an empty schema and every query would fail.
#
# Set RUN_MIGRATIONS=false to skip (only one container should migrate to avoid
# two processes racing to create the same tables on a fresh database).
# =============================================================================

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  # Alembic reads settings.DATABASE_URL (assembled from DATABASE_HOST/PORT/
  # USER/PASSWORD/NAME), so it targets whatever DB this container points at.
  echo "[entrypoint] Running database migrations (alembic upgrade head)..."
  attempts=0
  max_attempts=30
  until alembic upgrade head; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge "$max_attempts" ]; then
      echo "[entrypoint] FAILED to apply database migrations after ${max_attempts} attempts." >&2
      exit 1
    fi
    echo "[entrypoint] Database not ready, retrying in 2s (attempt ${attempts}/${max_attempts})..."
    sleep 2
  done
  echo "[entrypoint] Database migrations complete."
fi

# Execute the container command (uvicorn, celery worker, celery beat, ...).
exec "$@"
