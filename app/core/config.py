# app/core/config.py
"""
Backend Core Configuration
Phase 1 — Section 2.3
Land Intelligence System
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All configuration for the Land Intelligence System backend.
    """
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    # File Storage Configuration
    FILE_STORAGE_PATH: str = Field(default="./file-storage", env="FILE_STORAGE_PATH")
    
    # Backup Configuration
    BACKUP_BASE_PATH: str = Field(default="./backups", env="BACKUP_BASE_PATH")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        """Pydantic configuration for settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()