-- =============================================================================
-- Land Intelligence — Supabase database setup (run in the Supabase SQL Editor)
-- =============================================================================
-- The backend's spatial models use geoalchemy2 `Geometry(POLYGON, srid=4326)`
-- columns and PostGIS functions, so the PostGIS extension MUST be enabled
-- BEFORE the first `alembic upgrade head` runs against this database.
--
-- Supabase installs PostGIS into the `extensions` schema. We add `extensions`
-- to the search_path of the roles the app/alembic connect as, otherwise the
-- `geometry` type and PostGIS functions won't resolve.
-- =============================================================================

-- 1) Enable PostGIS in the dedicated `extensions` schema (idempotent).
create extension if not exists postgis with schema extensions;

-- 2) Allow the relevant roles to use the extensions schema.
--    The backend connects with the database password you set for the
--    `postgres` role (or a dedicated DB user you create in Supabase).
grant usage on schema extensions to postgres, anon, authenticated, service_role;

-- 3) Make the `extensions` schema (where PostGIS types live) part of the
--    default search_path for the app connection roles so `geometry` resolves.
alter role postgres set search_path to public, extensions;
alter role service_role set search_path to public, extensions;
alter role authenticator set search_path to public, extensions;

-- 4) (Recommended) If you created a dedicated application DB role/user for the
--    backend (e.g. `land_backend`), grant it the schema usage too and add the
--    extensions schema to its search_path. Uncomment and adjust as needed:
-- grant usage on schema extensions to land_backend;
-- alter role land_backend set search_path to public, extensions;

-- 5) Verify PostGIS is available.
select PostGIS_Full_Version();
