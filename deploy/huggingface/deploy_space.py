# =============================================================================
# deploy/huggingface/deploy_space.py — Create + deploy the backend to a HF Space
# =============================================================================
# Automates:
#   1. Creating a Hugging Face Space (repo_type=space, sdk=docker).
#   2. Setting all required environment variables / secrets on the Space.
#   3. Uploading the staged Space folder (deploy/huggingface/build/) to the repo.
#
# NOTE: Hugging Face now requires a PRO subscription to host Docker Spaces
# (public or private). Run `prepare_space.ps1` first to stage the build folder.
#
# Usage (from repo root):
#   $env:HF_TOKEN = "<hf_...>"
#   $env:DATABASE_HOST / PORT / NAME / USER / PASSWORD = "<supabase values>"
#   $env:SECRET_KEY = "<random-32+-char>"
#   .\venv\Scripts\python.exe deploy/huggingface/deploy_space.py
#
# Optional env overrides:
#   HF_SPACE_ID    (default: Ananie2024/land-intelligence-backend)
#   HF_BUILD_DIR   (default: deploy/huggingface/build)
#   DATABASE_PORT  (default: 5432)  DATABASE_NAME (default: postgres)
#   ENVIRONMENT    (default: production)   LOG_LEVEL (default: INFO)
#   START_REDIS    (default: true)         RUN_MIGRATIONS (default: true)
# =============================================================================
import os
import secrets as psecrets
import sys
import urllib3
from pathlib import Path

import requests

# Corporate TLS-proxy environment: Python's trust store doesn't include the
# proxy root CA (Windows tooling trusts it). Disable verification for this
# deployment script only.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.Session.verify = False

from huggingface_hub import HfApi  # noqa: E402


def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required env var: {name}")
    return value


def main() -> None:
    token = required("HF_TOKEN")
    space_id = os.environ.get("HF_SPACE_ID", "Ananie2024/land-intelligence-backend")
    build_dir = os.environ.get(
        "HF_BUILD_DIR",
        str(Path(__file__).resolve().parent / "build"),
    )

    secrets = {
        "ENVIRONMENT": os.environ.get("ENVIRONMENT", "production"),
        "PORT": os.environ.get("PORT", "7860"),
        "API_PORT": os.environ.get("API_PORT", "7860"),
        "DATABASE_HOST": required("DATABASE_HOST"),
        "DATABASE_PORT": os.environ.get("DATABASE_PORT", "5432"),
        "DATABASE_NAME": os.environ.get("DATABASE_NAME", "postgres"),
        "DATABASE_USER": required("DATABASE_USER"),
        "DATABASE_PASSWORD": required("DATABASE_PASSWORD"),
        "DATABASE_ECHO": os.environ.get("DATABASE_ECHO", "false"),
        "SECRET_KEY": os.environ.get("SECRET_KEY") or psecrets.token_hex(32),
        "CORS_ORIGINS": os.environ.get(
            "CORS_ORIGINS",
            '["https://land-intelligence-frontend.vercel.app",'
            ' "https://ananie2024-land-intelligence-backend.hf.space"]',
        ),
        "START_REDIS": os.environ.get("START_REDIS", "true"),
        "REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "RUN_MIGRATIONS": os.environ.get("RUN_MIGRATIONS", "true"),
        "UVICORN_WORKERS": os.environ.get("UVICORN_WORKERS", "1"),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
        "FILE_STORAGE_PATH": os.environ.get("FILE_STORAGE_PATH", "/app/file-storage"),
        "BACKUP_BASE_PATH": os.environ.get("BACKUP_BASE_PATH", "/app/backups"),
        "LOG_FILE_PATH": os.environ.get("LOG_FILE_PATH", "/app/logs/app.log"),
    }

    api = HfApi(token=token)

    # 1) Ensure the Space exists.
    try:
        api.create_repo(repo_id=space_id, repo_type="space", space_sdk="docker", private=False)
        print(f"[1/3] Space '{space_id}' created.")
    except Exception as exc:  # already exists, or another failure
        print(f"[1/3] create_repo returned: {exc}")

    # 2) Set secrets (idempotent — overrides existing values).
    print("[2/3] Setting Space secrets...")
    for key, value in secrets.items():
        try:
            api.add_space_secret(repo_id=space_id, key=key, value=value)
            print(f"      {key}=<set>")
        except Exception as exc:
            print(f"      {key} FAILED: {exc}")

    # 3) Upload the staged Space folder.
    print(f"[3/3] Uploading build folder: {build_dir}")
    if not Path(build_dir).exists():
        raise SystemExit(
            f"Build folder not found: {build_dir}. Run prepare_space.ps1 first."
        )
    api.upload_folder(folder_path=build_dir, repo_id=space_id, repo_type="space")

    print(f"\nDeployed! Space: https://huggingface.co/spaces/{space_id}")
    print(f"App URL     : https://{space_id.lower().replace('/', '-')}.hf.space")


if __name__ == "__main__":
    main()