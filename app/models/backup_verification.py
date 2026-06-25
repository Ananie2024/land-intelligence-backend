import enum
from sqlalchemy import Column, String, DateTime
from sqlalchemy import UUID

from app.models.base import BaseModel


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class BackupVerification(BaseModel):
    __tablename__ = "backup_verifications"

    backup_job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String, nullable=True)
    status = Column(String, default=VerificationStatus.PENDING.value, nullable=False)
    notes = Column(String, nullable=True)

    def __repr__(self):
        return f"<BackupVerification(id={self.id}, backup_job_id={self.backup_job_id}, status={self.status})>"
