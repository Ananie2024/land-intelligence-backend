# Land Intelligence — Multi-Platform Deployment

This folder contains **new, deployment-only** configuration files for running the
Land Intelligence & Stewardship System across three managed platforms:

| Component | Platform | Config location | Docs |
|-----------|----------|-----------------|------|
| Database (PostgreSQL + PostGIS) | **Supabase** | `supabase/` | [supabase/README.md](supabase/README.md) |
| Backend API (FastAPI) | **Hugging Face Spaces** (Docker SDK) | `huggingface/` | [huggingface/README.md](huggingface/README.md) |
| Frontend (Vite / React) | **Vercel** | `../land-intelligence-frontend/` (vercel.json) | [vercel/README.md](vercel/README.md) |

> **Important:** Nothing in this folder, or the new frontend files
> (`vercel.json`, `.nvmrc`, `.env.production.example`), changes how the app runs
> **locally**. The local development setup (root `Dockerfile`,
> `docker-compose.yml`, `.env.example`, `vite.config.ts`) is left **untouched**.
> These files are additive deployment artifacts only.

## Architecture Overview

```
        +----------------------------------------------+
        |  Vercel (frontend)                            |
        |  Vite/React static build (dist/)              |
        |  VITE_API_URL -> HF Space                     |
        +-----------------------+----------------------+
                                |  HTTPS  (browser -> HF Space)
                                v
        +----------------------------------------------+
        |  Hugging Face Spaces (backend)               |
        |  FastAPI/uvicorn on port 7860                |
        |  - reads Supabase via asyncpg (DATABASE_URL) |
        |  - optional in-container redis for JWT       |
        |    token blacklist (fails open if absent)    |
        +-----------------------+----------------------+
                                |  internet (SSL)
                                v
        +----------------------------------------------+
        |  Supabase (PostgreSQL + PostGIS)             |
        |  postgis extension enabled (extensions.sql)  |
        +----------------------------------------------+
```

## Recommended Deployment Order

1. **Supabase** — create the project, run `extensions.sql` to enable PostGIS,
   and capture the database connection details.
2. **Hugging Face Spaces** — create the Docker Space, set the env vars (using
   the Supabase connection + `PORT=7860`), and deploy the backend.
3. **Vercel** — import `land-intelligence-frontend/`, set `VITE_API_URL` to the
   HF Space URL, and deploy the frontend.

See each platform folder for the specific steps, files, and environment
variables.
