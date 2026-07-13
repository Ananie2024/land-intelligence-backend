"""merge migrations

Revision ID: 032eaed0a76e
Revises: 8a7b6c5d4e3f, a1b2c3d4e5f7, b2c3d4e5f6a7
Create Date: 2026-07-13 15:34:50.979238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '032eaed0a76e'
down_revision: Union[str, None] = ('8a7b6c5d4e3f', 'a1b2c3d4e5f7', 'b2c3d4e5f6a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
