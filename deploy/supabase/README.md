# Land Intelligence — Supabase Database Deployment

This folder contains everything needed to deploy the **Land Intelligence &
Stewardship System** database to **Supabase** (PostgreSQL + PostGIS).

## ✅ Current state (as of the last deploy)

The database is deployed and live on Supabase:

| Field            | Value                                                       |
|------------------|-------------------------------------------------------------|
| Account          | Ananie2024 / anahafasha@gmail.com                            |
| Project name     | `land-intelligence-db`                                       |
| **Project ref**  | `brlcynrinbcdgrrdcirm`                                       |
| Region           | `eu-west-1` (West EU / Ireland)                              |
| Database         | `postgres`                                                   |
| PostGIS          | enabled (`postgis` 3.3.7)                                    |
| Alembic head     | `73e159f607a7` (stamped)                                     |
| Tables created   | 16 (audit_logs, backup_jobs, backup_verifications, document_types, documents, land_use_categories, parcel_ownership_history, parcels, parishes, physical_locations, qr_code_registry, storage_cabinets, tax_payments, tax_records, users, alembic_version) |

### Connection (session pooler, IPv4)

```
host     : aws-1-eu-west-1.pooler.supabase.com
port     : 5432   (session)  /  6543 (transaction pooler)
database : postgres
user     : postgres.brlcynrinbcdgrrdcirm
password : <the database password set at creation>
```

> The pooler host for this (newer) project is **`aws-1-eu-west-1…`** (note `aws-1`,
> not `aws-0`). Newer projects are not routed on the legacy `aws-0-*` poolers.

---

## How the schema was deployed

Because the Alembic migration **history is not runnable from an empty database**
(the "clean" base migration already bakes in the final schema, so several later
additive migrations—e.g. `e8f7a6b5c4d3` adding `documents.metadata`—fail on a
fresh DB), the schema was bootstrapped directly from the SQLAlchemy **models**
(the app's source of truth), then Alembic was **stamped** at head so future
`alembic upgrade head` runs are clean no-ops.

```
1. Enable PostGIS          -> extensions.sql (idempotent)
2. Build schema from models -> deploy/supabase/bootstrap_schema.py
3. Stamp alembic at head    -> version 73e159f607a7
```

### Files

| File                     | Purpose                                                                  |
|--------------------------|--------------------------------------------------------------------------|
| `extensions.sql`         | Idempotent setup — enables `postgis` in the `extensions` schema and adds it to `search_path`. |
| `schema.sql`             | Reference DDL generated from Alembic (`alembic upgrade head --sql`). **Inspection only** (see caveat below). |
| `bootstrap_schema.py`    | **Deployment script** — builds the schema from the app models, adds the spatial GiST index, and stamps Alembic at head. |
| `.env.supabase.example`  | Template for Supabase connection variables (Hugging Face docs link here). |
| `deploy.ps1`             | Optional helper that wires local env vars and runs the bootstrap.       |

## Re-running / updating the schema

### Fresh deployment (empty database)

```powershell
# set connection env vars, then:
# 1) one-time PostGIS
$env:PGPASSWORD = "<db-password>"
psql -h aws-1-eu-west-1.pooler.supabase.com -p 5432 -U postgres.brlcynrinbcdgrrdcirm -d postgres -f deploy/supabase/extensions.sql

# 2) build schema from models + stamp head
$env:DATABASE_HOST     = "aws-1-eu-west-1.pooler.supabase.com"
$env:DATABASE_PORT     = "5432"
$env:DATABASE_NAME     = "postgres"
$env:DATABASE_USER     = "postgres.brlcynrinbcdgrrdcirm"
$env:DATABASE_PASSWORD = "<db-password>"
$env:SECRET_KEY        = "<random-32+-char>"
.\venv\Scripts\python.exe deploy/supabase/bootstrap_schema.py
```

> **Warning:** `bootstrap_schema.py` drops the `public` schema (CASCADE) and
> recreates it. Only run it on an **empty/ephemeral** database.

### Adding a new migration later

Once the DB is stamped at head, append new migrations as usual and run
`alembic upgrade head`. Do not try to re-run the full history on a brand-new
empty DB from scratch (it fails for the reasons above).


## About the migration caveat

Two fixes to the migration files were made to reduce fresh-DB failures, but the
history is still not fully self-consistent from empty:

- `b2c3d4e5f6a7` (`rename_parcel_number_to_upi`): changed `down_revision` from
  `a1b2c3d4e5f6` to `a3bfa1088a59` so the rename always runs **after** the
  `a3bfa1088a59` UUID-conversion migration (which still references
  `parcel_number`). Previously Alembic could run the rename first and break it.
- `8a7b6c5d4e3f` (`recreate_users_table_with_uuid`): removed the invalid
  `CREATE TYPE IF NOT EXISTS userrole ...` — PostgreSQL does not support
  `IF NOT EXISTS` on `CREATE TYPE`, and `sa.Enum(...)` already creates the type.

These make the chain closer to correct but do **not** make it fully runnable from
empty (e.g. `e8f7a6b5c4d3` still conflicts with the base migration).

## Secrets / security notes

- Never commit `.env`, `.env.supabase`, or the database password.
- The GitHub workflow [`.github/workflows/deploy-database.yml`](../../.github/workflows/deploy-database.yml)
  runs `alembic upgrade head` on demand using repository **secrets**
  (`DATABASE_HOST/PORT/NAME/USER/PASSWORD`, `SECRET_KEY`). Use the `aws-1` pooler
  values above for this project.

## Connection reference for this project

| Mode                    | Host                                  | Port | User                          |
|-------------------------|---------------------------------------|------|-------------------------------|
| Session pooler (reco.)  | `aws-1-eu-west-1.pooler.supabase.com` | 5432 | `postgres.brlcynrinbcdgrrdcirm` |
| Transaction pooler      | `aws-1-eu-west-1.pooler.supabase.com` | 6543 | `postgres.brlcynrinbcdgrrdcirm` |
| Direct (IPv6 only)      | `db.brlcynrinbcdgrrdcirm.supabase.co` | 5432 | `postgres`                    |

