# syntax=docker/dockerfile:1
# =============================================================================
# Land Intelligence & Stewardship System — Hugging Face Space image
# -----------------------------------------------------------------------------
# Production Docker image for running the FastAPI backend on Hugging Face
# Spaces (Docker SDK). It is designed to be deployed with the repo root as the
# build context (app/, alembic/, alembic.ini, requirements.txt present):
#
#   docker build -f deploy/huggingface/Dockerfile -t land-intelligence-hf .
#
# The HF entrypoint (entrypoint.sh) runs `alembic upgrade head` against the
# configured database (Supabase) and then serves the API on $PORT (7860).
# =============================================================================

###############################################################################
# STAGE 1 — BUILDER
###############################################################################
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Build-time system packages required by native wheels/sources
# (psycopg2, argon2-cffi, cryptography, pyproj/shapely, bcrypt, ...).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

###############################################################################
# STAGE 2 — RUNTIME
###############################################################################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME="/app" \
    PORT=7860

# Runtime system libraries:
#   libpq5        PostgreSQL client library (asyncpg / psycopg2)
#   curl          health-check / debugging
#   redis-server  optional local Redis for the JWT token blacklist (see entrypoint)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_HOME}

# Copy the fully-built virtualenv from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy application code (context root must contain these, see above).
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# HF Space entrypoint: migrations then uvicorn on $PORT.
COPY entrypoint.sh ./
RUN chmod +x ${APP_HOME}/entrypoint.sh

# Runtime writable directories.
# NOTE: HF Spaces free tier provides EPHEMERAL disk — files written here
# (uploads, backups) do NOT persist across restarts. Use GCS/B2 for durable
# object storage if you need persistence.
RUN mkdir -p \
        ${APP_HOME}/file-storage \
        ${APP_HOME}/backups \
        ${APP_HOME}/logs \
        ${APP_HOME}/temp

# HF Spaces routes external traffic to this port.
EXPOSE 7860

CMD ["/app/entrypoint.sh"]
