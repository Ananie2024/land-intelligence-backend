# app/api/v1/routes/gis_analysis.py
# app/api/v1/routes/gis_analysises.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_gis_analysises():
    return {
        "message": "Gis_analysis endpoints not implemented yet"
    }