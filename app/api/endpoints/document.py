import os
import shutil
from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.mongo_service import get_all_documents, insert_document
from app.utils.file_processing import process_file
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/documents/")
async def list_documents():
    """Récupère tous les documents."""
    documents = await get_all_documents()
    return {"documents": documents}