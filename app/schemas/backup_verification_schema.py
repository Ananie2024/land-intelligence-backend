from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.backup_verification import VerificationStatus


class BackupVerificationBase(BaseModel):
    backup_job_id: str
    verified_by: Optional[str] = None
    status: VerificationStatus = VerificationStatus.PENDING
    notes: Optional[str] = None


class BackupVerificationCreate(BackupVerificationBase):
    pass


class BackupVerificationUpdate(BaseModel):
    verified_by: Optional[str] = None
    status: Optional[VerificationStatus] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class BackupVerificationInDBBase(BackupVerificationBase):
    verified_at: datetime

    class Config:
        from_attributes = True


class BackupVerificationInDB(BackupVerificationInDBBase):
    pass
