# Deploying the Database to Supabase

Supabase provides a managed **PostgreSQL** database and supports the
**PostGIS** extension, which this application requires for its spatial
(`Geometry(POLYGON, srid=4326)`) columns and GIS analysis.

## Files

- `extensions.sql` — run once in the Supabase SQL Editor to enable PostGIS.
- `.env.supabase.example` — template for the backend connection settings.

## Setup Steps

1. **Create a Supabase project**
   - Go to <https://supabase.com/dashboard> → **New project**.
   - Note the **Project URL** (`https://<project-ref>.supabase.co`) — the
     `<project-ref>` is used in the connection host.

2. **Enable PostGIS**
   - Open **SQL Editor** and run the contents of [`extensions.sql`](extensions.sql).
   - This installs `postgis` into the `extensions` schema and adds that schema
     to the connection roles' `search_path` so the `geometry` type resolves.

3. **Get the connection details**
   - **Project Settings → Database → Connection string**.
   - Copy the **Direct connection** (or **Session pooler**) credentials:
     - `Host`: `db.<project-ref>.supabase.co`
     - `Port`: `5432`
     - `Database`: `postgres`
     - `User`: `postgres`
     - `Password`: (the database password you configured)
   - > ⚠️ Avoid the **Transaction pooler** (port `6543`). The app uses
     > `asyncpg`, which relies on prepared statements incompatible with
     > transaction pooling. Use the direct or session-pooled connection.

4. **Run the database migrations (Alembic)**
   - Set the Supabase environment values (from `.env.supabase.example`) either
     as local env vars or in the HF Space settings, then run:
     ```bash
     alembic upgrade head
     ```
   - On Hugging Face Spaces, migrations run automatically on deploy via
     `deploy/huggingface/entrypoint.sh`.

5. **Optional: dedicated DB role**
   - For better security you can create a dedicated role in Supabase, grant it
     usage on `extensions`, and point `DATABASE_USER`/`DATABASE_PASSWORD` at it.
     (See the commented grants in `extensions.sql`.)

## Connecting the backends

- **Hugging Face Space** → copy `DATABASE_*` values from
  `.env.supabase.example` into the Space's environment variables
  (see `../huggingface/README.md`).
- **Local CLI / manual** → copy them into a local `.env` (the `deploy/supabase`
  template is the `.env` equivalent). The root `.env` used for local Postgres
  development is left unchanged.
