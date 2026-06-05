# app/api/v1/routes/documents.py
# app/api/v1/routes/documentes.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_documents():
    return {
        "message": "Document endpoints not implemented yet"
    }