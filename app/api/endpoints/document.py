from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.core.database import database  
from app.services.mongo_service import get_all_documents
from app.services.excel_service import process_excel_file, save_chunks_to_db

router = APIRouter()

class ExcelRequest(BaseModel):
    file_name: str

@router.post("/process_excel/")
async def process_excel(request: ExcelRequest):
    """
    Endpoint pour traiter un fichier Excel et sauvegarder les chunks dans MongoDB.
    Args:
        request (ExcelRequest): Objet contenant le nom du fichier Excel.
    """
    # Traiter le fichier Excel
    result = process_excel_file(request.file_name)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Extraire les pages et les sauvegarder dans MongoDB
    processed_data = result["processed_data"]
    all_chunks = []
    for sheet_data in processed_data:
        chunk_data = {
            "sheet_name": sheet_data["sheet_name"],
            "data": sheet_data["data"],  # Contenu de la page
            "embedding": sheet_data["embedding"],  # Embedding vectorisé
        }
        all_chunks.append(chunk_data)
    
    # Sauvegarde dans MongoDB
    db_result = await save_chunks_to_db(all_chunks, collection_name="test-chunks")
    if db_result["status"] == "error":
        raise HTTPException(status_code=500, detail=db_result["message"])
    
    return {"status": "success", "message": db_result["message"]}
