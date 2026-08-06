# syntax=docker/dockerfile:1
# =============================================================================
# Land Intelligence & Stewardship System — Backend Image
# -----------------------------------------------------------------------------
# Multi-stage production build for the FastAPI + Celery backend.
#
# One image is produced and is capable of running every backend role by
# overriding the container command:
#   * API         -> uvicorn app.main:app
#   * Celery      -> celery -A app.tasks.celery_app worker
#   * Celery Beat -> celery -A app.tasks.celery_app beat
#
# Build:
#   docker build -t land-intelligence-backend:latest .
# =============================================================================

###############################################################################
# STAGE 1 — BUILDER
# Compiles / installs all Python dependencies into an isolated virtualenv.
# Keeps the build toolchain (C compiler, headers) out of the final image.
###############################################################################
FROM python:3.11-slim AS builder

# Python hardening: no .pyc bytecode, unbuffered stdout/stderr for logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Build-time system packages required by native Python wheels/sources
# (e.g. psycopg2, bcrypt, argon2-cffi, cryptography, pyproj/shapely wheels).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install dependencies first so the heavy layer is cached unless
# requirements.txt changes (fast iterative rebuilds).
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

###############################################################################
# STAGE 2 — RUNTIME
# Slim production image with no compiler toolchain.
###############################################################################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME="/app"

# Runtime-only system libraries and utilities.
# libpq5: PostgreSQL client library (asyncpg / psycopg2-binary).
# curl:   used by the container HEALTHCHECK.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application securely.
RUN groupadd -r appuser \
    && useradd -r -g appuser -d /home/appuser appuser

# Copy the fully-built virtualenv from the builder stage.
COPY --from=builder /opt/venv /opt/venv

WORKDIR ${APP_HOME}

# Copy application code.
# Alembic is required at runtime so migrations can be run inside the container.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Runtime writable directories (bind/volume these in production to persist).
RUN mkdir -p \
        ${APP_HOME}/file-storage \
        ${APP_HOME}/backups \
        ${APP_HOME}/logs \
        ${APP_HOME}/temp \
    && chown -R appuser:appuser ${APP_HOME}

# Run as an unprivileged user.
USER appuser

# FastAPI API port.
EXPOSE 8000

# Healthcheck against the liveness endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health/live > /dev/null || exit 1

# ---------------------------------------------------------------------
# Default command: run the FastAPI application with Uvicorn.
# Override CMD in docker-compose to launch Celery worker / beat instead.
# ---------------------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
