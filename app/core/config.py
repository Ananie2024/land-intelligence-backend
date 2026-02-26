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
    
    # File Storage Configuration
    FILE_STORAGE_PATH: str = Field(default="./file-storage")
    
    # Backup Configuration
    BACKUP_BASE_PATH: str = Field(default="./backups")
    
   # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE_PATH: str = Field(default="./logs/app.log")
    LOG_MAX_BYTES: int = Field(default=10485760)  # 10 MB
    LOG_BACKUP_COUNT: int = Field(default=5)
settings = Settings()