# app/models/base.py
"""
Base Model Classes
Land Intelligence System
"""
from sqlalchemy import Column, DateTime, Boolean, func, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when record was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when record was last updated"
    )


class SoftDeleteMixin:
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=func.true(),
        comment="Soft delete flag: True if record is active, False if deleted"
    )


class UUIDMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="UUID primary key"
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, UUIDMixin):
    __abstract__ = True

    # ← use __tablename__ as plain classvar, not declared_attr
    # Each model defines its own __tablename__ explicitly anyway
    # so this fallback is just a safety net
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '__tablename__') or cls.__tablename__ is None:
            cls.__tablename__ = cls.__name__.lower()

    def dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"