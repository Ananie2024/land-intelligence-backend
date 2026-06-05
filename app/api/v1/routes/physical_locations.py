# app/api/v1/routes/physical_locations.py
# app/api/v1/routes/physical_locationses.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_physical_locations():
    return {
        "message": "Physical_locations endpoints not implemented yet"
    }