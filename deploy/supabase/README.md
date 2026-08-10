# Land Intelligence — Supabase Database Deployment

This folder contains everything needed to deploy the **Land Intelligence &
Stewardship System** database to **Supabase** (PostgreSQL + PostGIS).

## Target project

| Field      | Value                                                        |
|------------|--------------------------------------------------------------|
| Account    | Ananie2024 / anahafasha@gmail.com                             |
| Org        | Ananie2024's Org                                              |
| Project id | `jbaohbvvjsfmhmvlsufb`                                        |
| Database   | `postgres`                                                    |
| Extension  | PostGIS (`postgis`) — **required** for the spatial models    |

> The backend's spatial models use `Geometry(POLYGON, 4326)` and
> `Geometry(MULTIPOLYGON, 4326)` columns (via GeoAlchemy2). The `postgis`
> extension **must be enabled before** the first `alembic upgrade head`, and the
> `extensions` schema must be on the connecting role's `search_path`.

## What's in this folder

| File                     | Purpose                                                                  |
|--------------------------|--------------------------------------------------------------------------|
| `extensions.sql`         | Idempotent setup — enables `postgis` in the `extensions` schema and adds it to `search_path`. Run **once**, in the Supabase SQL Editor. |
| `schema.sql`             | Reference DDL generated from Alembic (`alembic upgrade head --sql`). **Inspection only.** |
| `.env.supabase.example`  | Template for Supabase connection variables (Hugging Face docs link here). |
| `deploy.ps1`             | Optional helper that wires local env vars into `alembic` runs.           |

## Recommended approach: run Alembic against the live Supabase DB

Alembic is the source of truth for the schema. Prefer running migrations against
the Supabase database directly instead of applying a static SQL dump.

### Prerequisites

- Locally reachable `psql`/network to the Supabase pooler host.
- The **database password** for the `postgres` role (or a dedicated role), found at
  *Project Settings → Database*. This is **different** from your Supabase account
  login password.
- Python venv with app deps installed (`pip install -r requirements.txt`).

### 1. Enable PostGIS (one time)

In the Supabase **SQL Editor**, run the contents of
[`extensions.sql`](extensions.sql). Verify with:

```sql
select PostGIS_Full_Version();
```

### 2. Point the connection at Supabase

The app config (`app/core/config.py`) builds `DATABASE_URL` from
`DATABASE_HOST / PORT / NAME / USER / PASSWORD`. Provide those as environment
variables when running Alembic.

Use the **session pooler** (IPv4, stable) — the direct `db.<ref>.supabase.co`
host is IPv6-only and may be unreachable from normal networks:

```powershell
# PowerShell quick run from the repo root
$env:DATABASE_HOST = "aws-0-<REGION>.pooler.supabase.com"
$env:DATABASE_PORT = "5432"
$env:DATABASE_NAME = "postgres"
$env:DATABASE_USER = "postgres.jbaohbvvjsfmhmvlsufb"
$env:DATABASE_PASSWORD = "<your-database-password>"
$env:SECRET_KEY      = "<random-32+-char-secret>"   # required by Settings
.\venv\Scripts\python.exe -m alembic upgrade head
```

The pooler region must match your project's region (see the connection string in
the dashboard). If you get
`FATAL: (ENOTFOUND) tenant/user postgres.jbaohbvvjsfmhmvlsufb not found`, the
region is wrong — copy the exact host from
*Project Settings → Database → Session pooler*.

### 3. Verify

```powershell
.\venv\Scripts\python.exe -m alembic current   # should show the latest head (73e159f607a7)
```

Then confirm the spatial plumbing:

```sql
-- in Supabase SQL Editor
select extname from pg_extension where extname = 'postgis';
select count(*) from information_schema.tables where table_schema = 'public';
```

## Alternative: Supabase CLI (`supabase db push`)

If you prefer the CLI (requires `SUPABASE_ACCESS_TOKEN` for non-interactive auth,
or `supabase login` in a browser session):

```powershell
supabase link --project-ref jbaohbvvjsfmhmvlsufb
supabase db push          # applies schema
# extensions.sql must still be run once via the SQL editor / psql first.
```

## Secrets / security notes

- Never commit `.env`, `.env.supabase`, or the database password.
- The GitHub workflow [`.github/workflows/deploy-database.yml`](../../.github/workflows/deploy-database.yml)
  runs `alembic upgrade head` on demand using repository **secrets**
  (`DATABASE_HOST/PORT/NAME/USER/PASSWORD`, `SECRET_KEY`).
- The onboarding flow (users, parishes, etc.) has no seed data required; the
  app manages inserts at runtime.

## Connection reference for this project

| Mode                    | Host                                   | Port | User                       |
|-------------------------|----------------------------------------|------|----------------------------|
| Session pooler (reco.)  | `aws-0-<REGION>.pooler.supabase.com`   | 5432 | `postgres.jbaohbvvjsfmhmvlsufb` |
| Transaction pooler      | `aws-0-<REGION>.pooler.supabase.com`   | 6543 | `postgres.jbaohbvvjsfmhmvlsufb` |
| Direct (IPv6 only)      | `db.jbaohbvvjsfmhmvlsufb.supabase.co`  | 5432 | `postgres`                 |

Replace `<REGION>` with the project's region (from the dashboard connection
string) and use your real database password.
