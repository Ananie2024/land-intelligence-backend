"""Change failed_login_attempts to Integer and tax monetary columns to Numeric

Revision ID: 63dbbad0300d
Revises: 9058171496f9
Create Date: 2026-06-26 11:30:36.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '63dbbad0300d'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change failed_login_attempts from String(10) to Integer
    op.execute('ALTER TABLE users ALTER COLUMN failed_login_attempts DROP DEFAULT')
    op.execute('ALTER TABLE users ALTER COLUMN failed_login_attempts TYPE INTEGER USING failed_login_attempts::integer')
    op.alter_column('users', 'failed_login_attempts',
               existing_type=sa.Integer(),
               type_=sa.Integer(),
               existing_nullable=False,
               existing_server_default=sa.text("'0'::integer"))

    # Change tax_records monetary columns from Float to Numeric(15, 2)
    op.alter_column('tax_records', 'assessed_value',
               existing_type=sa.Float(),
               type_=sa.Numeric(15, 2),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'tax_rate_applied',
               existing_type=sa.Float(),
               type_=sa.Numeric(15, 2),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'base_tax_amount',
               existing_type=sa.Float(),
               type_=sa.Numeric(15, 2),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'penalties_amount',
               existing_type=sa.Float(),
               type_=sa.Numeric(15, 2),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'total_amount',
               existing_type=sa.Float(),
               type_=sa.Numeric(15, 2),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    # Change tax_payments.payment_amount from Float to Numeric(15, 2)
    op.alter_column('tax_payments', 'payment_amount',
               existing_type=sa.Float(),
               type_=sa.Numeric(15, 2),
               existing_nullable=False)


def downgrade() -> None:
    # Revert tax_payments.payment_amount
    op.alter_column('tax_payments', 'payment_amount',
               existing_type=sa.Numeric(15, 2),
               type_=sa.Float(),
               existing_nullable=False)

    # Revert tax_records monetary columns
    op.alter_column('tax_records', 'total_amount',
               existing_type=sa.Numeric(15, 2),
               type_=sa.Float(),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'penalties_amount',
               existing_type=sa.Numeric(15, 2),
               type_=sa.Float(),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'base_tax_amount',
               existing_type=sa.Numeric(15, 2),
               type_=sa.Float(),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'tax_rate_applied',
               existing_type=sa.Numeric(15, 2),
               type_=sa.Float(),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    op.alter_column('tax_records', 'assessed_value',
               existing_type=sa.Numeric(15, 2),
               type_=sa.Float(),
               existing_nullable=False,
               existing_server_default=sa.text("'0.0'::double precision"))

    # Revert failed_login_attempts
    op.alter_column('users', 'failed_login_attempts',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False,
               existing_server_default=sa.text("'0'"))