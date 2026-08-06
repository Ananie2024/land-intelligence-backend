# Supabase Deployment Guide
Land Intelligence & Stewardship System

This guide walks you through deploying the backend database on **Supabase** (hosted PostgreSQL + PostGIS).

---

## 1. Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign in / create an account.
2. Click **New Project**.
3. Choose an organization, name the project (e.g. `land-intelligence`), set a strong database password, and select a region close to your users (Africa / Europe recommended for Rwanda).
4. Wait for the project to finish provisioning (~1–2 minutes).

---

## 2. Enable PostGIS

The app uses GeoAlchemy2 (`Geometry` columns on parcels). PostGIS is required.

1. In the Supabase dashboard go to **Database → Extensions**.
2. Search for `postgis` and enable it.
3. (Optional but recommended) also enable `postgis_topology` and `uuid-ossp` if not already on.

You can also run this in the **SQL Editor**:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 3. Get Connection Strings

Go to **Project Settings → Database**.

You will see two important connection strings:

### A. Direct connection (port 5432) — best for migrations & local development
```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```
or the classic form:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### B. Connection Pooler – Transaction mode (port 6543) — best for the running FastAPI app
```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Recommendation**
- Use the **direct** connection for Alembic migrations.
- Use the **pooler (Transaction mode)** for the FastAPI application in production.

The code in `app/core/database.py` automatically detects the pooler (port 6543 / `pooler.supabase.com`) and switches to `NullPool` + disables prepared statements.

---

## 4. Configure Environment Variables

Copy `.env.example` → `.env` and fill in the Supabase values:

```env
# -----------------------------------------------------------------------------
# DATABASE (Supabase)
# -----------------------------------------------------------------------------
DATABASE_HOST=db.[PROJECT-REF].supabase.co          # or the pooler host
DATABASE_PORT=5432                                  # 5432 = direct | 6543 = pooler
DATABASE_NAME=postgres
DATABASE_USER=postgres                              # or postgres.[PROJECT-REF] for pooler
DATABASE_PASSWORD=your-supabase-db-password
DATABASE_ECHO=False

# Full URL is assembled automatically by config.py as:
# postgresql://{user}:{password}@{host}:{port}/{name}
```

Or you can set the individual fields and the app will build `DATABASE_URL`.

**Important security notes**
- Never commit the real `.env`.
- Rotate the database password if it ever leaks.
- Prefer the pooler URL for the long-running API process.

---

## 5. Run Migrations

From your local machine (or CI):

```bash
# Make sure .env points to the *direct* connection (port 5432)
alembic upgrade head
```

Verify tables exist in the Supabase **Table Editor**.

---

## 6. Test the Connection

Start the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs and hit the `/health` or any protected endpoint after login.

---

## 7. (Optional) Supabase Storage for Documents

Later you can replace the local filesystem with Supabase Storage buckets for land titles, contracts, etc. The current code still uses local paths (`FILE_STORAGE_PATH`). This can be a follow-up task.

---

## 8. Next Deployment Steps (after DB is live)

1. Deploy the FastAPI app (Railway, Render, Fly.io, DigitalOcean App Platform, or a VPS).
2. Set the same environment variables in the hosting platform.
3. Point the frontend `VITE_API_URL` to the new backend URL.
4. Configure CORS_ORIGINS for the production frontend domain.
5. Set up Redis (Upstash is a good free option) for token blacklist + Celery if needed.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `prepared statement already exists` | You are using the pooler but statement cache is not disabled. Make sure you are on the latest `database.py`. |
| Connection timeout / IPv6 issues | Enable the **IPv4 add-on** in Supabase or use the pooler. |
| PostGIS functions missing | Re-run `CREATE EXTENSION postgis;` |
| Alembic fails with SSL | Add `?sslmode=require` to the URL if needed. |

---

**You're ready.** Create the project, enable PostGIS, paste the credentials into `.env`, run migrations, and the backend is live on Supabase.
