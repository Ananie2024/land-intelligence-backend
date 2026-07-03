"""Recreate users table with UUID after a3bfa1088a59 dropped it

Revision ID: 8a7b6c5d4e3f
Revises: a3bfa1088a59
Create Date: 2026-07-03 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8a7b6c5d4e3f'
down_revision: Union[str, None] = 'a3bfa1088a59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    """Create users table with UUID primary key and userrole enum."""
    # Create the userrole enum type first (if not exists)
    op.execute("CREATE TYPE IF NOT EXISTS userrole AS ENUM ('admin', 'client', 'viewer')")
    
    op.create_table('users',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='UUID primary key'),
        sa.Column('email', sa.VARCHAR(length=255), nullable=False, comment='User email address'),
        sa.Column('username', sa.VARCHAR(length=100), nullable=False, comment='Unique username'),
        sa.Column('hashed_password', sa.VARCHAR(length=255), nullable=False, comment='Bcrypt hashed password'),
        sa.Column('full_name', sa.VARCHAR(length=255), nullable=True, comment='Full name of user'),
        sa.Column('role', sa.Enum('admin', 'client', 'viewer', name='userrole'), nullable=False, server_default='viewer', comment='User role (admin, client, viewer)'),
        sa.Column('parish_id', sa.UUID(), nullable=True, comment='For clients, links to their parish'),
        sa.Column('is_active', sa.BOOLEAN(), server_default=sa.text('true'), nullable=False, comment='Whether user account is active'),
        sa.Column('is_verified', sa.BOOLEAN(), server_default=sa.text('false'), nullable=False, comment='Whether email is verified'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True, comment='Last successful login timestamp'),
        sa.Column('failed_login_attempts', sa.INTEGER(), server_default=sa.text('0'), nullable=False, comment='Count of failed login attempts'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True, comment='Account locked until this timestamp'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


def downgrade() -> None:
    """Drop users table and enum type."""
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    # Only drop type if no other tables are using it
    op.execute("DROP TYPE IF EXISTS userrole")