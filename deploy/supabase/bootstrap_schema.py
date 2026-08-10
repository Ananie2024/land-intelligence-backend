# =============================================================================
# deploy/supabase/bootstrap_schema.py
# =============================================================================
# One-time bootstrap used to deploy the Land Intelligence schema to a FRESH
# target database (e.g. a brand-new Supabase project) directly from the app
# models, then stamp Alembic at the head revision.
#
# Why this exists:
#   The Alembic migration chain has a pre-existing fresh-DB ordering bug
#   (migration a3bfa1088a59 references `parcels.parcel_number`/`idx_parcel_number`
#   after the rename migration b2c3d4e5f6a7 renamed the column to `upi` and the
#   index to `idx_parcel_upi`). Running `alembic upgrade head` from an empty
#   database fails with "index idx_parcel_number does not exist".
#
#   For a brand-new database with no data this script instead creates the exact
#   final schema from the SQLAlchemy models (the source of truth), then records
#   the head revision in alembic_version so future `alembic upgrade head` runs
#   (including the CI workflow) are clean no-ops.
#
# Safety: only use on an EMPTY database. It drops the `public` schema (CASCADE)
# and recreates it, so it will DESTROY any existing data.
#
# Usage (from repo root, with env pointing at the target DB):
#   $env:DATABASE_HOST=... ; $env:DATABASE_PORT=5432 ; $env:DATABASE_NAME=postgres
#   $env:DATABASE_USER=... ; $env:DATABASE_PASSWORD=... ; $env:SECRET_KEY=...
#   .\venv\Scripts\python.exe deploy/supabase/bootstrap_schema.py
# =============================================================================
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.models import import_all_models
from app.models.base import Base

HEAD = "73e159f607a7"  # current alembic head


def main() -> None:
    import_all_models()

    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    print(f"Connecting to: {url.split('@')[-1]}")
    engine = create_engine(url)

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        # Make PostGIS types (in the extensions schema) resolvable.
        conn.execute(text("ALTER ROLE postgres SET search_path TO public, extensions"))

    print("Creating tables from models...")
    Base.metadata.create_all(engine)

    # Recreate the spatial GiST index on parcels.geometry_wkb (defined in the
    # migrations as idx_parcels_geometry but not declared on the model).
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_parcels_geometry "
                "ON parcels USING gist (geometry_wkb)"
            )
        )

    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version ("
                " version_num VARCHAR(32) NOT NULL,"
                " CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
            )
        )
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:h)"), {"h": HEAD}
        )

    print(f"Done. Schema created and stamped to Alembic head: {HEAD}")


if __name__ == "__main__":
    main()
