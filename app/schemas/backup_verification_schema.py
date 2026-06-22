from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.backup_verification import VerificationStatus


class BackupVerificationBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    backup_job_id: str
    verified_by: Optional[str] = None
    status: VerificationStatus = VerificationStatus.PENDING
    notes: Optional[str] = None


class BackupVerificationCreate(BackupVerificationBase):
    pass


class BackupVerificationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    verified_by: Optional[str] = None
    status: Optional[VerificationStatus] = None
    notes: Optional[str] = None


class BackupVerificationInDBBase(BackupVerificationBase):
    id: str
    verified_at: datetime
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class BackupVerificationInDB(BackupVerificationInDBBase):
    pass
