# app/main.py

"""
FastAPI Application Bootstrap
Phase 1 — Section 2.5
Land Intelligence System
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.endpoints import router as v1_router
from app.api.middleware.authentication import AuthenticationMiddleware
from app.api.middleware.logging_middleware import LoggingMiddleware
from app.api.middleware.error_handlers import register_error_handlers
from app.core.config import settings
from app.core.database import engine, get_db
from app.core.logging_config import setup_logging


# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------

setup_logging()
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# FastAPI Application
# ------------------------------------------------------------------

app = FastAPI(
    title="Land Intelligence System API",
    version="1.0.0",
    description="""
    Digital Land Management System for the Archdiocese of Kigali.

    This API provides secure access to land parcel records,
    document management, GIS spatial analysis,
    tax calculation, and backup services.
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


# ------------------------------------------------------------------
# Error Handlers
# ------------------------------------------------------------------

# Register before middleware stack
register_error_handlers(app)


# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "CORS_ORIGINS", []),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Custom Middleware
# ------------------------------------------------------------------

app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthenticationMiddleware)


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

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint that verifies database connectivity.
    """

    db_status = "unhealthy"

    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            db_status = "healthy"
            break

    except Exception as e:
        logger.error(
            f"Database health check failed: {str(e)}"
        )

    return {
        "status": (
            "healthy"
            if db_status == "healthy"
            else "degraded"
        ),
        "api": "healthy",
        "database": db_status,
        "version": "1.0.0",
    }


# ------------------------------------------------------------------
# Startup Events
# ------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks.
    """

    logger.info(
        "Starting Land Intelligence System API"
    )

    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            logger.info(
                "Database connection verified"
            )
            break

    except Exception as e:
        logger.error(
            f"Failed to connect to database on startup: {str(e)}"
        )

        # Do not crash application startup
        # Allows degraded startup if database
        # becomes available shortly afterward.


# ------------------------------------------------------------------
# Shutdown Events
# ------------------------------------------------------------------

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks.
    """

    logger.info(
        "Shutting down Land Intelligence System API"
    )

    await engine.dispose()