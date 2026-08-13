"""add lease and tax tables

Revision ID: f2a4c9d1b3e7
Revises: 73e159f607a7
Create Date: 2026-08-13 12:00:00.000000

Adds the table schemas introduced by the leasing and custom-rate tax work:

- lease_agreements
- lease_payment_schedules
- tax_records
- tax_payments

These were never added to the migration chain when the models were committed,
so the new /tax and /leases endpoints fail with "relation does not exist".

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f2a4c9d1b3e7'
down_revision: Union[str, None] = '73e159f607a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _enums():
    """Return the native PostgreSQL enum types used by the new tables."""
    return [
        postgresql.ENUM(
            'monthly', 'quarterly', 'semi_annually', 'annually',
            name='paymentfrequency',
        ),
        postgresql.ENUM(
            'draft', 'active', 'expired', 'terminated', 'renewed',
            name='leasestatus',
        ),
        postgresql.ENUM(
            'pending', 'paid', 'overdue', 'partial', 'cancelled',
            name='leasepaymentstatus',
        ),
        postgresql.ENUM(
            'pending', 'paid', 'overdue', 'cancelled',
            name='taxrecordstatus',
        ),
    ]


def upgrade() -> None:
    binding = op.get_bind()

    # Create enum types up front with checkfirst so re-runs / partial applies
    # are idempotent.
    for enum in _enums():
        enum.create(binding, checkfirst=True)

    # The hosted (Supabase) database was bootstrapped from the SQLAlchemy models
    # and already contains the tax_* tables (with all of their indexes), so guard
    # each table's creation on existence. This keeps the migration runnable both
    # on a fresh database (creates all four tables) and against the existing
    # hosted schema (creates only the missing lease tables).
    existing_tables = set(sa.inspect(binding).get_table_names())

    if 'lease_agreements' not in existing_tables:
        op.create_table(
            'lease_agreements',
            sa.Column('id', postgresql.UUID(as_uuid=True),
                      server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('parcel_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('lease_number', sa.String(length=100), nullable=False),
            sa.Column('tenant_name', sa.String(length=255), nullable=False),
            sa.Column('tenant_contact', sa.String(length=255), nullable=True),
            sa.Column('tenant_id_number', sa.String(length=100), nullable=True),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=False),
            sa.Column('annual_rent_amount', sa.Numeric(15, 2),
                      server_default='0.00', nullable=False),
            sa.Column('payment_frequency', postgresql.ENUM(name='paymentfrequency', create_type=False),
                      server_default='annually', nullable=False),
            sa.Column('installment_amount', sa.Numeric(15, 2),
                      server_default='0.00', nullable=False),
            sa.Column('status', postgresql.ENUM(name='leasestatus', create_type=False),
                      server_default='active', nullable=False),
            sa.Column('purpose_use', sa.String(length=500), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['parcel_id'], ['parcels.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('lease_number'),
        )
        op.create_index('ix_lease_agreements_parcel_id', 'lease_agreements', ['parcel_id'])
        op.create_index('idx_lease_number', 'lease_agreements', ['lease_number'])
        op.create_index('idx_tenant_name', 'lease_agreements', ['tenant_name'])
        op.create_index('idx_lease_status', 'lease_agreements', ['status'])
        op.create_index('idx_lease_start_end', 'lease_agreements', ['start_date', 'end_date'])

    if 'lease_payment_schedules' not in existing_tables:
        op.create_table(
            'lease_payment_schedules',
            sa.Column('id', postgresql.UUID(as_uuid=True),
                      server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('lease_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('due_date', sa.Date(), nullable=False),
            sa.Column('amount_due', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('amount_paid', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('status', postgresql.ENUM(name='leasepaymentstatus', create_type=False),
                      server_default='pending', nullable=False),
            sa.Column('paid_date', sa.Date(), nullable=True),
            sa.Column('payment_reference', sa.String(length=100), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['lease_id'], ['lease_agreements.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_lease_payment_schedules_lease_id', 'lease_payment_schedules', ['lease_id'])
        op.create_index('ix_lease_payment_schedules_due_date', 'lease_payment_schedules', ['due_date'])
        op.create_index('ix_lease_payment_schedules_status', 'lease_payment_schedules', ['status'])
        op.create_index('idx_lease_schedule_due', 'lease_payment_schedules', ['lease_id', 'due_date'])
        op.create_index('idx_lease_schedule_status', 'lease_payment_schedules', ['status'])
    if 'tax_records' not in existing_tables:
        op.create_table(
            'tax_records',
            sa.Column('id', postgresql.UUID(as_uuid=True),
                      server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('parcel_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('assessment_year', sa.Integer(), nullable=False),
            sa.Column('assessed_value', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('tax_rate_applied', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('base_tax_amount', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('penalties_amount', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('total_amount', sa.Numeric(15, 2), server_default='0.00', nullable=False),
            sa.Column('status', postgresql.ENUM(name='taxrecordstatus', create_type=False),
                      server_default='pending', nullable=False),
            sa.Column('due_date', sa.Date(), nullable=False),
            sa.Column('paid_date', sa.Date(), nullable=True),
            sa.Column('payment_reference', sa.String(length=100), nullable=True),
            sa.Column('notes', sa.String(length=500), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['parcel_id'], ['parcels.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_tax_records_parcel_id', 'tax_records', ['parcel_id'])
        op.create_index('ix_tax_records_assessment_year', 'tax_records', ['assessment_year'])
        op.create_index('ix_tax_records_status', 'tax_records', ['status'])
        op.create_index('idx_assessment_year', 'tax_records', ['assessment_year'])
        op.create_index('idx_status', 'tax_records', ['status'])
        op.create_index('idx_due_date', 'tax_records', ['due_date'])
        op.create_index('idx_unique_parcel_year', 'tax_records', ['parcel_id', 'assessment_year'], unique=True)
    if 'tax_payments' not in existing_tables:
        op.create_table(
            'tax_payments',
            sa.Column('id', postgresql.UUID(as_uuid=True),
                      server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('tax_record_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('payment_amount', sa.Numeric(15, 2), nullable=False),
            sa.Column('payment_date', sa.Date(), nullable=False),
            sa.Column('payment_method', sa.String(length=50), nullable=False),
            sa.Column('payment_reference', sa.String(length=100), nullable=True),
            sa.Column('receipt_number', sa.String(length=50), nullable=False),
            sa.Column('received_by', sa.String(length=200), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('is_reversal', sa.Boolean(), server_default='0', nullable=False),
            sa.Column('reversed_payment_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['tax_record_id'], ['tax_records.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['reversed_payment_id'], ['tax_payments.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('payment_reference'),
            sa.UniqueConstraint('receipt_number'),
        )
        op.create_index('ix_tax_payments_tax_record_id', 'tax_payments', ['tax_record_id'])
        op.create_index('ix_tax_payments_payment_date', 'tax_payments', ['payment_date'])
        op.create_index('ix_tax_payments_payment_reference', 'tax_payments', ['payment_reference'])
        op.create_index('ix_tax_payments_receipt_number', 'tax_payments', ['receipt_number'])
        op.create_index('idx_payment_date', 'tax_payments', ['payment_date'])
        op.create_index('idx_payment_method', 'tax_payments', ['payment_method'])
        op.create_index('idx_receipt_number', 'tax_payments', ['receipt_number'])


def downgrade() -> None:
    binding = op.get_bind()

    op.drop_index('idx_receipt_number', table_name='tax_payments')
    op.drop_index('idx_payment_method', table_name='tax_payments')
    op.drop_index('idx_payment_date', table_name='tax_payments')
    op.drop_index('ix_tax_payments_receipt_number', table_name='tax_payments')
    op.drop_index('ix_tax_payments_payment_reference', table_name='tax_payments')
    op.drop_index('ix_tax_payments_payment_date', table_name='tax_payments')
    op.drop_index('ix_tax_payments_tax_record_id', table_name='tax_payments')
    op.drop_table('tax_payments')

    op.drop_index('idx_unique_parcel_year', table_name='tax_records')
    op.drop_index('idx_due_date', table_name='tax_records')
    op.drop_index('idx_status', table_name='tax_records')
    op.drop_index('idx_assessment_year', table_name='tax_records')
    op.drop_index('ix_tax_records_status', table_name='tax_records')
    op.drop_index('ix_tax_records_assessment_year', table_name='tax_records')
    op.drop_index('ix_tax_records_parcel_id', table_name='tax_records')
    op.drop_table('tax_records')

    op.drop_index('idx_lease_schedule_status', table_name='lease_payment_schedules')
    op.drop_index('idx_lease_schedule_due', table_name='lease_payment_schedules')
    op.drop_index('ix_lease_payment_schedules_status', table_name='lease_payment_schedules')
    op.drop_index('ix_lease_payment_schedules_due_date', table_name='lease_payment_schedules')
    op.drop_index('ix_lease_payment_schedules_lease_id', table_name='lease_payment_schedules')
    op.drop_table('lease_payment_schedules')

    op.drop_index('idx_lease_start_end', table_name='lease_agreements')
    op.drop_index('idx_lease_status', table_name='lease_agreements')
    op.drop_index('idx_tenant_name', table_name='lease_agreements')
    op.drop_index('idx_lease_number', table_name='lease_agreements')
    op.drop_index('ix_lease_agreements_parcel_id', table_name='lease_agreements')
    op.drop_table('lease_agreements')

    for enum in reversed(_enums()):
        enum.drop(binding, checkfirst=True)
