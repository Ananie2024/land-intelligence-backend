# app/main.py
"""
FastAPI Application Bootstrap
Phase 1 — Section 2.5
Land Intelligence System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1.endpoints import router as v1_router
from app.api.middleware.authentication import AuthenticationMiddleware
from app.api.middleware.logging_middleware import LoggingMiddleware
from app.api.middleware.error_handlers import register_error_handlers
from app.core.config import settings
from app.core.database import engine, get_db
from app.core.logging_config import setup_logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Land Intelligence System API",
    version="1.0.0",
    description="""
    Digital Land Management System for the Archidiocese of Kigali.
    
    This API provides secure access to land parcel records, document management,
    GIS spatial analysis, tax calculation, and backup services.
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthenticationMiddleware)

# Register error handlers
register_error_handlers(app)

# Include API routers
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies database connectivity.
    
    Returns:
        dict: Status of the API and database connection
    """
    db_status = "unhealthy"
    try:
        # Attempt to get a database session and execute a simple query
        async for db in get_db():
            await db.execute("SELECT 1")
            db_status = "healthy"
            break
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "api": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Execute actions on application startup."""
    logger.info("Starting Land Intelligence System API")
    # Verify database connection on startup
    try:
        async for db in get_db():
            await db.execute("SELECT 1")
            logger.info("Database connection verified")
            break
    except Exception as e:
        logger.error(f"Failed to connect to database on startup: {str(e)}")
        # Don't raise - let the app try to recover


@app.on_event("shutdown")
async def shutdown_event():
    """Execute actions on application shutdown."""
    logger.info("Shutting down Land Intelligence System API")
    # Cleanup database connections
    await engine.dispose()