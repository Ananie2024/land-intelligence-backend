# app/core/logging_config.py
"""
Logging Configuration
Phase 1 — Section 2.3
Land Intelligence System
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from app.core.config import settings


from contextvars import ContextVar

# Context variable for correlation ID (async-safe)
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds correlation ID if present in context.
    """
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add correlation_id from contextvars
        log_record['correlation_id'] = correlation_id_ctx.get()


def setup_logging() -> None:
    """
    Configure structured logging with rotation.
    Sets up both console and file handlers with JSON formatting.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(module)s %(function)s %(line)s %(message)s %(correlation_id)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file_path = Path(settings.LOG_FILE_PATH)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log startup
    logging.info("Logging configured", extra={
        "log_level": settings.LOG_LEVEL,
        "log_file": str(log_file_path)
    })


def get_correlation_id() -> str:
    """
    Get correlation ID from contextvars.
    """
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID in contextvars.
    """
    correlation_id_ctx.set(correlation_id)