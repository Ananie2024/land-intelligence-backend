"""spatial_optimization

Revision ID: 315a1f2b3c4d
Revises: c2341b14cb56
Create Date: 2026-06-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '315a1f2b3c4d'
down_revision: Union[str, None] = 'c2341b14cb56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- PARCELS TABLE ---
    # 1. Add temporary binary column
    op.add_column('parcels', sa.Column('temp_geom', sa.LargeBinary(), nullable=True))
    
    # 2. Convert hex string to binary
    op.execute("UPDATE parcels SET temp_geom = UNHEX(geometry_wkb) WHERE geometry_wkb IS NOT NULL AND geometry_wkb != ''")
    
    # 3. Recreate as GEOMETRY to ensure clean SRID 4326
    op.add_column('parcels', sa.Column('geometry_new', Geometry(geometry_type='POLYGON', srid=4326), nullable=True))
    
    # 4. Populate new geometry column
    op.execute("UPDATE parcels SET geometry_new = ST_GeomFromWKB(temp_geom, 4326) WHERE temp_geom IS NOT NULL")
    
    # 5. Add SPATIAL INDEX
    op.create_index('idx_parcel_geometry', 'parcels', ['geometry_new'], mysql_prefix='SPATIAL')
    
    # 6. Cleanup parcels
    op.drop_column('parcels', 'geometry_wkb')
    op.drop_column('parcels', 'temp_geom')
    op.alter_column('parcels', 'geometry_new', new_column_name='geometry_wkb', existing_type=Geometry(geometry_type='POLYGON', srid=4326))

    # --- PARISHES TABLE ---
    # 1. Add boundary_wkb column as GEOMETRY MULTIPOLYGON SRID 4326
    op.add_column('parishes', sa.Column('boundary_wkb', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True))
    
    # 2. Add SPATIAL INDEX for parish boundaries
    op.create_index('idx_parish_boundary', 'parishes', ['boundary_wkb'], mysql_prefix='SPATIAL')


def downgrade() -> None:
    # --- PARISHES TABLE ---
    op.drop_index('idx_parish_boundary', table_name='parishes')
    op.drop_column('parishes', 'boundary_wkb')

    # --- PARCELS TABLE ---
    # 1. Add back the TEXT column
    op.add_column('parcels', sa.Column('geometry_old', sa.Text(), nullable=True, comment='Spatial geometry in WKB format (hex)'))
    
    # 2. Convert GEOMETRY back to hex string
    op.execute("UPDATE parcels SET geometry_old = HEX(ST_AsWKB(geometry_wkb)) WHERE geometry_wkb IS NOT NULL")
    
    # 3. Drop spatial column and index
    op.drop_index('idx_parcel_geometry', table_name='parcels')
    op.drop_column('parcels', 'geometry_wkb')
    
    # 4. Rename back
    op.alter_column('parcels', 'geometry_old', new_column_name='geometry_wkb', existing_type=sa.Text())
