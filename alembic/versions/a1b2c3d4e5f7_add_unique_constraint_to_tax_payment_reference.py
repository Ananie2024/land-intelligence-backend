"""Add unique constraint to tax_payment.payment_reference

Revision ID: a1b2c3d4e5f7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-07 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint to payment_reference column."""
    # Create unique index on payment_reference column
    op.create_unique_constraint(
        'tax_payments_payment_reference_key',
        'tax_payments',
        ['payment_reference']
    )


def downgrade() -> None:
    """Remove unique constraint from payment_reference column."""
    op.drop_constraint(
        'tax_payments_payment_reference_key',
        'tax_payments',
        type_='unique'
    )