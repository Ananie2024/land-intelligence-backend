# app/api/v1/routes/parcels.py
# app/api/v1/routes/parcelses.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_parcels():
    return {
        "message": "Parcels endpoints not implemented yet"
    }