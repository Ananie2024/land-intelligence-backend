# app/api/v1/routes/qr_codes.py
# app/api/v1/routes/qr_codeses.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_qr_codes():
    return {
        "message": "Qr_codes endpoints not implemented yet"
    }