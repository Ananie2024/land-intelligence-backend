from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.backup_job import BackupJobStatus


class BackupJobBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    job_type: str
    status: BackupJobStatus = Field(default=BackupJobStatus.PENDING)
    tier: str
    source_path: Optional[str] = None
    destination_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_count: Optional[int] = None
    checksum: Optional[str] = None
    error_message: Optional[str] = None


class BackupJobCreate(BackupJobBase):
    pass


class BackupJobUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    job_type: Optional[str] = None
    status: Optional[BackupJobStatus] = None
    tier: Optional[str] = None
    source_path: Optional[str] = None
    destination_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_count: Optional[int] = None
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BackupJobInDBBase(BackupJobBase):
    id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class BackupJobInDB(BackupJobInDBBase):
    pass
