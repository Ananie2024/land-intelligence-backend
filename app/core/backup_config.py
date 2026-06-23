# app/core/backup_config.py
# app/core/backup_config.py
"""
Backup Configuration
Land Intelligence System

Central constants and path helpers for the 3-2-1 backup strategy:
  - 3 copies of data
  - 2 different storage types (local + cloud)
  - 1 offsite copy (GCS or Backblaze B2)
"""

from pathlib import Path
from app.core.config import settings


class BackupJobType:
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    DIFFERENTIAL = "DIFFERENTIAL"
    RESTORE = "RESTORE"


class BackupTier:
    LOCAL = "local"
    CLOUD_GCS = "cloud_gcs"
    CLOUD_B2 = "cloud_b2"


RETENTION_POLICY: dict[str, int] = {
    BackupTier.LOCAL: 7,
    BackupTier.CLOUD_GCS: 30,
    BackupTier.CLOUD_B2: 30,
}


def get_local_backup_root() -> Path:
    return Path(settings.BACKUP_BASE_PATH).resolve()


def get_database_backup_dir() -> Path:
    path = get_local_backup_root() / "database"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_filesystem_backup_dir() -> Path:
    path = get_local_backup_root() / "filesystem"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_backup_dir() -> Path:
    path = get_local_backup_root() / "config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cloud_staging_dir(provider: str) -> Path:
    path = get_local_backup_root() / "cloud_staging" / provider
    path.mkdir(parents=True, exist_ok=True)
    return path