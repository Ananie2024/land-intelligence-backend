import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.backup_job import BackupJobStatus


class BackupJobBase(BaseModel):
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
    id: uuid.UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BackupJobInDB(BackupJobInDBBase):
    pass
