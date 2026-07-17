# app/core/config.py
"""
Application Settings
Land Intelligence System
"""
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    # Set to "production" in deployment.  Used to enable/disable
    # safety checks that should not run during local development.
    ENVIRONMENT: str = Field(default="development")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)

    # ------------------------------------------------------------------
    # Database — individual fields (matches .env structure)
    # ------------------------------------------------------------------
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_NAME: str = Field(default="land_intelligence_db")
    DATABASE_USER: str = Field(default="land_user")

    # Required — no silent empty-password fallback
    DATABASE_PASSWORD: str = Field(...)

    # Set to True in .env to log all SQL statements during development
    DATABASE_ECHO: bool = Field(default=False)

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL(self) -> str:
        """
        Full PostgreSQL DSN, assembled from individual fields.
        Used by both SQLAlchemy (via database.py) and Alembic (via env.py).
        """
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(...)

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    # Development default: Swagger UI only.
    # For the JavaFX desktop frontend add "http://localhost:8080".
    # Never use ["*"] with allow_credentials=True in production.
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:8000"])

    # ------------------------------------------------------------------
    # File Storage
    # ------------------------------------------------------------------
    FILE_STORAGE_PATH: str = Field(default="./file-storage")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    ALLOWED_EXTENSIONS: list[str] = Field(
        default=[".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"]
    )

    # ------------------------------------------------------------------
    # Redis (used for token blacklist and caching)
    # ------------------------------------------------------------------
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Security: When True, fail-closed mode for token blacklist
    # During Redis outages, revoked tokens will be treated as invalid
    # When False (default), availability is prioritized (revoked tokens may still work)
    SECURITY_CRITICAL_MODE: bool = Field(default=False)

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------
    BACKUP_BASE_PATH: str = Field(default="./backups")
    GCS_ENABLED: bool = Field(default=False)
    GCS_PROJECT_ID: str | None = Field(default=None)
    GCS_BUCKET_NAME: str | None = Field(default=None)
    GCS_CREDENTIALS_PATH: str | None = Field(default=None)
    GCS_ENCRYPTION_KEY_PATH: str | None = Field(default=None)
    GCS_ENCRYPTION_ENABLED: bool = Field(default=False)
    B2_ENABLED: bool = Field(default=False)
    B2_ACCOUNT_ID: str | None = Field(default=None)
    B2_APPLICATION_KEY: str | None = Field(default=None)
    B2_BUCKET_NAME: str | None = Field(default=None)
    B2_ENCRYPTION_KEY_PATH: str | None = Field(default=None)
    B2_ENCRYPTION_ENABLED: bool = Field(default=False)

    # ------------------------------------------------------------------
    # SMTP / Email
    # ------------------------------------------------------------------
    SMTP_SERVER: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_USE_TLS: bool = Field(default=True)
    EMAIL_SENDER: str | None = Field(default=None)
    BACKUP_NOTIFICATION_EMAILS: list[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE_PATH: str = Field(default="./logs/app.log")
    LOG_MAX_BYTES: int = Field(default=10_485_760)  # 10 MB
    LOG_BACKUP_COUNT: int = Field(default=5)


settings = Settings()