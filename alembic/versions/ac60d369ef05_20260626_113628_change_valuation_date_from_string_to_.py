"""Change valuation_date from String to Date

Revision ID: ac60d369ef05
Revises: 63dbbad0300d
Create Date: 2026-06-26 11:36:28.473232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ac60d369ef05'
down_revision: Union[str, None] = '63dbbad0300d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert valuation_date from String(10) to Date
    op.execute('ALTER TABLE parcels ALTER COLUMN valuation_date TYPE DATE USING valuation_date::date')
    op.alter_column('parcels', 'valuation_date',
               existing_type=sa.String(length=10),
               type_=sa.Date(),
               existing_nullable=True)


def downgrade() -> None:
    # Revert valuation_date back to String(10)
    op.alter_column('parcels', 'valuation_date',
               existing_type=sa.Date(),
               type_=sa.String(length=10),
               existing_nullable=True)