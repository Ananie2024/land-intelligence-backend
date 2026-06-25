# app/models/backup_job.py

import enum
from sqlalchemy import Column, DateTime, BigInteger, String

from app.models.base import BaseModel


class BackupJobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BackupJob(BaseModel):
    __tablename__ = "backup_jobs"

    job_type = Column(String, nullable=False)  # e.g., FULL, INCREMENTAL, DIFFERENTIAL, RESTORE
    status = Column(String(20), default=BackupJobStatus.PENDING.value, nullable=False)
    tier = Column(String, nullable=False)  # e.g., local, cloud_gcs, cloud_b2
    source_path = Column(String, nullable=True)
    destination_path = Column(String, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    file_count = Column(BigInteger, nullable=True)
    checksum = Column(String, nullable=True) # e.g., MD5, SHA256 of the backup manifest
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    def __repr__(self):
        return f"<BackupJob(id={self.id}, job_type={self.job_type}, status={self.status})>"
