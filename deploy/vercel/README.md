# Deploying the Frontend to Vercel

The frontend is a standard **Vite / React** app located in
`land-intelligence-frontend/`. It is deployed to **Vercel** as a static site a
nd talks to the backend hosted on **Hugging Face Spaces**.

## New files (deployment-only)

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel config: builds with `npm run build`, outputs `dist/`, SPA rewrite to `index.html`. |
| `.nvmrc` | Pins the Node.js version (`22`) for reproducible builds. |
| `.env.production.example` | Template for the production `VITE_API_URL` and flags. |

> These are **additive** — no local-development frontend files are changed.

## Setup steps

1. **Import the project into Vercel**
   - In the Vercel dashboard: **Add New → Project**, connect the git repo, then
     set **Root Directory** to `land-intelligence-frontend`.
   - Vercel auto-detects Vite; the `vercel.json` pins the build/install behavior.

2. **Set environment variables** (Production)
   - **Settings → Environment Variables** (Production), using
     [`.env.production.example`](../land-intelligence-frontend/.env.production.example):
     - `VITE_API_URL=https://<your-username>-land-intelligence-backend.hf.space`
     - `VITE_APP_NAME=Land Intelligence`
     - `VITE_ENABLE_DEBUG=false`
   - Vite bakes `VITE_*` variables into the bundle at **build time**, so re-deploy
     after changing them.

3. **Deploy**
   - Vercel runs `npm run build` (`tsc -b && vite build` → `dist/`) automatically
     on push. The `vercel.json` `rewrites` send all non-file routes to
     `index.html` so client-side routing works.

4. **CORS on the backend**
   - Add your Vercel origin (`https://<your-app>.vercel.app`, plus any custom
     domain and `https://<project>.vercel.app` preview URLs) to the backend's
     `CORS_ORIGINS` in the Hugging Face Space variables. The backend rejects
     browser calls from origins it does not trust.

## Notes

- The axios client (`src/api/axios.ts`) uses a **relative** `/api/v1` base in
  development (via the Vite proxy) and `VITE_API_URL + /api/v1` in production,
  so no code changes are needed.
- Validation: `src/utils/env.ts` validates `VITE_API_URL` as a URL and
  `VITE_APP_NAME`/`VITE_ENABLE_DEBUG`. If validation fails in production it
  falls back to safe defaults rather than crashing the build.
- Node: `.nvmrc` pins `22`; Vite 8 / TypeScript 6 require Node 20.19+.
