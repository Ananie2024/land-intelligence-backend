from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    
    # Database Configuration
    DATABASE_URL: str = Field(...)
    
    # Security Configuration
    SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(default=["*"])

    # File Storage Configuration
    FILE_STORAGE_PATH: str = Field(default="./file-storage")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    ALLOWED_EXTENSIONS: list[str] = Field(default=[".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"])
    
    # Backup Configuration
    BACKUP_BASE_PATH: str = Field(default="./backups")
    GCS_ENABLED: bool = Field(default=False)
    GCS_PROJECT_ID: str | None = Field(default=None)
    GCS_BUCKET_NAME: str | None = Field(default=None)
    GCS_CREDENTIALS_PATH: str | None = Field(default=None)
    B2_ENABLED: bool = Field(default=False)
    B2_ACCOUNT_ID: str | None = Field(default=None)
    B2_APPLICATION_KEY: str | None = Field(default=None)
    B2_BUCKET_NAME: str | None = Field(default=None)
    
   # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE_PATH: str = Field(default="./logs/app.log")
    LOG_MAX_BYTES: int = Field(default=10485760)  # 10 MB
    LOG_BACKUP_COUNT: int = Field(default=5)
settings = Settings()
