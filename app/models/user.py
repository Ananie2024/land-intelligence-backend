# app/models/user.py
"""
User Model
Land Intelligence System
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, UUID, func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel


class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    CLIENT = "client"
    VIEWER = "viewer"


class User(BaseModel):
    """
    User account model for authentication and authorization.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]), 
     nullable=False, 
     default=UserRole.VIEWER )
    parish_id = Column(UUID(as_uuid=True), nullable=True)  # For clients, links to their parish
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(String(10), default="0")
    locked_until = Column(DateTime(timezone=True), nullable=True)
    # created_at, updated_at, is_active inherited from TimestampMixin/SoftDeleteMixin

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
