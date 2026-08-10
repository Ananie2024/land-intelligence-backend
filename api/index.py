# =============================================================================
# Vercel Python Function entrypoint — exposes the FastAPI app as an ASGI app.
# Vercel routes all traffic to this handler (see vercel.json rewrites).
# =============================================================================
import os
import sys

# Ensure the project root is importable (Vercel runs this file from the
# function bundle; `app/` lives at the repo root).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.main import app as app  # noqa: E402  (ASGI application for Vercel)