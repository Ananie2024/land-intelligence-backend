# app/api/v1/routes/parishes.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_backups():
    return {
        "message": "backups endpoints not implemented yet"
    }# app/api/v1/routes/backups.py
