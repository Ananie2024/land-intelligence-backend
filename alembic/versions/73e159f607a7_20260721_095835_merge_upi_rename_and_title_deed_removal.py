"""merge upi rename and title-deed removal

Revision ID: 73e159f607a7
Revises: e8f7a6b5c4d3, remove_title_deed_number
Create Date: 2026-07-21 09:58:35.952128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73e159f607a7'
down_revision: Union[str, None] = ('e8f7a6b5c4d3', 'remove_title_deed_number')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
