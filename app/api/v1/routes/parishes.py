# app/api/v1/routes/parishes.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_parishes():
    return {
        "message": "Parish endpoints not implemented yet"
    }# app/api/v1/routes/parishes.py
