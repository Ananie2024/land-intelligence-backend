# app/models/backup_job.py

import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, BigInteger, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class BackupJobStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String, nullable=False)  # e.g., FULL, INCREMENTAL, DIFFERENTIAL, RESTORE
    status = Column(Enum(BackupJobStatus), default=BackupJobStatus.PENDING, nullable=False)
    tier = Column(String, nullable=False)  # e.g., local, cloud_gcs, cloud_b2
    source_path = Column(String, nullable=True)
    destination_path = Column(String, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    file_count = Column(BigInteger, nullable=True)
    checksum = Column(String, nullable=True) # e.g., MD5, SHA256 of the backup manifest
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<BackupJob(id={self.id}, job_type={self.job_type}, status={self.status})>"
