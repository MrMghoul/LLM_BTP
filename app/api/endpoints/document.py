from fastapi import APIRouter, HTTPException
from app.services.mongo_service import get_all_documents

router = APIRouter()

@router.get("/documents/")
async def list_documents():
    """Récupère tous les documents."""
    documents = await get_all_documents()
    return {"documents": documents}