# app/main.py

"""
FastAPI Application Bootstrap
Phase 1 — Section 2.5
Land Intelligence System
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.endpoints import router as v1_router
from app.api.middleware.exception_handler import register_exception_handler
from app.api.middleware.response_middleware import StandardizeResponseMiddleware
from app.core.config import settings
from app.core.database import engine, get_db
from app.core.logging_config import setup_logging
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.rate_limit import limiter


# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------

setup_logging()
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager — replaces the deprecated
    @app.on_event("startup") / ("shutdown") pattern.
    """
    # --- STARTUP ------------------------------------------------------------
    logger.info("Starting Land Intelligence System API")

    # Production safety check: CORS origins
    if settings.ENVIRONMENT == "production":
        localhost_origins = [
            o for o in settings.CORS_ORIGINS
            if "localhost" in o or "127.0.0.1" in o
        ]
        if localhost_origins:
            logger.warning(
                "CORS_ORIGINS contains localhost entries in production "
                "environment: %s.  These are likely leftover development "
                "defaults.  Set CORS_ORIGINS to the actual frontend "
                "origin(s) in your .env or environment variables.",
                localhost_origins,
            )

    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            logger.info("Database connection verified")
            break
    except Exception as e:
        logger.error(f"Failed to connect to database on startup: {str(e)}")
        # Do not crash application startup

    yield  # <-- application runs here

    # --- SHUTDOWN -----------------------------------------------------------
    logger.info("Shutting down Land Intelligence System API")
    await engine.dispose()


# ------------------------------------------------------------------
# FastAPI Application
# ------------------------------------------------------------------

# Disable interactive API docs in production to avoid leaking endpoint
# schemas to unauthenticated users.
_docs_url = None if settings.ENVIRONMENT == "production" else "/api/docs"
_redoc_url = None if settings.ENVIRONMENT == "production" else "/api/redoc"
_openapi_url = None if settings.ENVIRONMENT == "production" else "/api/openapi.json"

app = FastAPI(
    title="Land Intelligence System API",
    version="1.0.0",
    description="""
    Digital Land Management System for the Archdiocese of Kigali.
    
    This API provides secure access to land parcel records,
    document management, GIS spatial analysis,
    tax calculation, and backup services.
    """,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
    lifespan=lifespan,
    redirect_slashes=False,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ------------------------------------------------------------------
# Exception Handler
# ------------------------------------------------------------------

# Register centralized exception handler
register_exception_handler(app)


# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add response standardization middleware
app.add_middleware(StandardizeResponseMiddleware)


# ------------------------------------------------------------------
# API Routers
# ------------------------------------------------------------------

app.include_router(v1_router, prefix="/api/v1")


# ------------------------------------------------------------------
# Root Endpoint
# ------------------------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    """
    API root endpoint.
    """
    return {
        "service": "Land Intelligence System API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/api/docs",
    }


# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------

@app.get("/health/live", tags=["System"])
async def health_live():
    """
    Liveness check to verify the API process is running.
    Returns the process status regardless of dependency health.
    """
    return {"status": "alive"}


@app.get("/health/ready", tags=["System"])
async def health_ready():
    """
    Readiness check to verify external dependencies (Database, Redis) are reachable.
    """
    db_status = "unhealthy"
    redis_status = "unhealthy"

    # Verify Database
    db_gen = get_db()
    try:
        async for db in db_gen:
            await db.execute(text("SELECT 1"))
            db_status = "healthy"
            break
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
    finally:
        await db_gen.aclose()

    # Verify Redis
    try:
        from app.core.token_blacklist import get_redis_client
        redis_client = get_redis_client()
        await redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")

    is_ready = db_status == "healthy" and redis_status == "healthy"
    status_code = 200 if is_ready else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_ready else "unhealthy",
            "api": "healthy",
            "database": db_status,
            "redis": redis_status,
            "version": "1.0.0",
        }
    )


@app.get("/health", tags=["System"])
async def health_check():
    """
    Fallback health check endpoint. Maps to readiness check for backwards compatibility.
    """
    return await health_ready()