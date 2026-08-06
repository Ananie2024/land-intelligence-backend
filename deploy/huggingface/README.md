---
title: Land Intelligence Backend
emoji: 🗺️
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Land Intelligence Backend (Hugging Face Space)

Runs the **FastAPI** backend for the Land Intelligence & Stewardship System as a
**Docker Space** on Hugging Face. It connects to a **Supabase** PostgreSQL
database and is called by the **Vercel**-hosted frontend.

## What this folder contains

| File | Purpose |
|------|---------|
| `Spacefile` | Declares this is a Docker Space listening on port `7860`. |
| `Dockerfile` | Production image (multi-stage) for the FastAPI backend. |
| `entrypoint.sh` | Runs migrations, optionally starts redis, then `uvicorn` on `$PORT`. |
| `.env.example` | Template for the Space environment variables. |
| `prepare_space.ps1` | Assembles this folder + backend source into a deployable Space root (`build/`). |

## ⚠️ Important: HF Spaces deploy the repo ROOT

Hugging Face Docker Spaces build the `Dockerfile` at the **root of the pushed
repository** — they cannot build one nested in a subfolder. Two options:

- **Option A (recommended):** run `prepare_space.ps1` to produce a standalone
  Space folder (`build/`) containing this folder's files plus `app/`, `alembic/`,
  `alembic.ini` and `requirements.txt`, then push that folder as the HF Space
  repo.
- **Option B:** create a dedicated Space repo whose root *is* the backend
  (copy `Dockerfile` + `entrypoint.sh` + `Spacefile` to its root along with the
  backend source).

You can also build/test the image locally with the repo root as context:

```bash
docker build -f deploy/huggingface/Dockerfile -t land-intelligence-hf .
```

## Prerequisites

1. A **Supabase** project with PostGIS enabled — run
   [`../supabase/extensions.sql`](../supabase/extensions.sql) in the Supabase
   SQL Editor **before** the first deploy (migrations depend on the `postgis`
   extension).
2. A **Hugging Face** account with Spaces enabled.

## Deploy steps

1. **Create the Space**
   - <https://huggingface.co/new-space> → type `Docker`, visibility of choice.
   - Keep the name, e.g. `land-intelligence-backend`.

2. **Stage a deployable folder** (Option A):
   ```powershell
   powershell -ExecutionPolicy Bypass -File deploy\huggingface\prepare_space.ps1
   ```
   Then push the generated `deploy\huggingface\build\` contents to the Space:
   ```bash
   cd deploy/huggingface/build
   git init && git add . && git commit -m "Deploy backend to HF Spaces"
   git remote add origin https://huggingface.co/spaces/<USER>/<SPACE>
   git push -u origin main
   ```

3. **Set environment variables**
   - **Settings → Variables and secrets → New variable**, using
     [`.env.example`](.env.example) as a guide.
   - At minimum: `ENVIRONMENT=production`, `DATABASE_HOST/PORT/NAME/USER/PASSWORD`
     (Supabase), `SECRET_KEY`, `CORS_ORIGINS` (your Vercel origin), and
     `START_REDIS=true` if you want the JWT token blacklist backed by in-Space
     redis.

4. **Verify**
   - Open the Space. The app serves on `https://<USER>-<SPACE>.hf.space`.
   - Health check: `https://<USER>-<SPACE>.hf.space/health/live`
   - Give Vercel this base URL as `VITE_API_URL`
     (`https://<USER>-<SPACE>.hf.space` — the axios client appends `/api/v1`).

## Platform notes & limitations

- **Port:** HF exposes the app on `$PORT` (default `7860`). The `Spacefile` sets
  `app_port: 7860` and the entrypoint binds to `$PORT`.
- **Ephemeral disk:** free Spaces do not persist the local filesystem. Uploaded
  documents and backups written to `/app/file-storage` / `/app/backups` are lost
  on restart. For durable storage configure GCS or Backblaze B2 (application
  currently supports `GCS_ENABLED` / `B2_ENABLED`).
- **Redis / Celery:** `START_REDIS=true` runs an in-memory redis for the JWT
  token blacklist only. Celery worker/beat are **not** started on the Space (no
  persistent broker / limited resources on free tier). Background/periodic jobs
  that rely on Celery will not run here unless you add them to `entrypoint.sh`.
- **Worker count:** keep `UVICORN_WORKERS=1` on free tier; raise on paid tiers.
