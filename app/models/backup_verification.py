import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class BackupVerification(Base):
    __tablename__ = "backup_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backup_job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    verified_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    verified_by = Column(String, nullable=True)
    status = Column(String, default=VerificationStatus.PENDING.value, nullable=False)
    notes = Column(String, nullable=True)

    def __repr__(self):
        return f"<BackupVerification(id={self.id}, backup_job_id={self.backup_job_id}, status={self.status})>"
