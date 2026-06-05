# app/api/v1/routes/tax_calculations.py
# app/api/v1/routes/tax_calculationses.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_tax_calculations():
    return {
        "message": "Tax_calculations endpoints not implemented yet"
    }