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


@router.post("/process-file-title/")
async def process_file_title_endpoint(file: UploadFile = File(...)):
    """Accepte un fichier et renvoie les chunks extraits en format JSON."""
    try:
        # Sauvegarder le fichier téléchargé temporairement
        temp_dir = os.path.join(os.path.expanduser("~"), "temp_files")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Traiter le fichier
        chunks = process_file(temp_file_path)
        
        # Supprimer le fichier temporaire
        os.remove(temp_file_path)
        
        # Insérer chaque chunk dans la base de données
        inserted_ids = []
        for chunk in chunks:
            document_id = await insert_document(chunk)
            inserted_ids.append(document_id)

        for chunk in chunks:
            if "_id" in chunk and isinstance(chunk["_id"], ObjectId):
                chunk["_id"] = str(chunk["_id"])  # Convertir en string
        
        return {"inserted_ids": inserted_ids, "chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

