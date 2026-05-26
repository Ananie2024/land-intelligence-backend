# app/models/audit_log.py
"""
Audit Log Model
Phase 2 — Section 3.1
Land Intelligence System
"""
from sqlalchemy import Column, String, DateTime, JSON, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import declared_attr
from app.models.base import BaseModel


class AuditLog(BaseModel):
    """
    Audit log entity representing immutable trail of all data changes.
    """

    __tablename__ = "audit_logs"

    table_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Name of the table that was modified"
    )

    record_id = Column(
        CHAR(36),
        nullable=False,
        index=True,
        comment="UUID of the record that was modified"
    )

    action = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Type of action (CREATE, UPDATE, DELETE, SOFT_DELETE, RESTORE)"
    )

    old_value = Column(
        JSON,
        nullable=True,
        comment="JSON representation of values before change"
    )

    new_value = Column(
        JSON,
        nullable=True,
        comment="JSON representation of values after change"
    )

    performed_by = Column(
        CHAR(36),
        nullable=False,
        index=True,
        comment="User ID who performed the action"
    )

    performed_at = Column(
        DateTime,
        nullable=False,
        index=True,
        comment="Timestamp when action was performed"
    )

    ip_address = Column(
        String(45),
        nullable=True,
        comment="IP address of the client"
    )

    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent string from client"
    )

    correlation_id = Column(
        String(36),
        nullable=True,
        index=True,
        comment="Request correlation ID for tracing"
    )

    # ← renamed Python attribute, DB column name stays 'metadata'
    audit_context = Column(
        "metadata",
        JSON,
        nullable=True,
        comment="JSON field for additional audit context"
    )

    # ← proper way to suppress updated_at for immutable audit logs
    @declared_attr
    def updated_at(cls):
        return None

    __table_args__ = (
        Index('idx_audit_table_record', 'table_name', 'record_id'),
        Index('idx_audit_performed_by_date', 'performed_by', 'performed_at'),
        Index('idx_audit_action_date', 'action', 'performed_at'),
        Index('idx_audit_correlation', 'correlation_id'),
    )

    def __repr__(self):
        return f"<AuditLog(table='{self.table_name}', action='{self.action}', record='{self.record_id}')>"