import os
import shutil
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from app.utils.file_processing import process_file
from app.services.chroma_service import add_document_chunk, get_all_documents, search_documents, store_document_chunks, search_documents_ranking

 
router = APIRouter()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Création du dossier d'upload s'il n'existe pas


# Modèle pour ajouter un chunk de document
class DocumentChunk(BaseModel):
    file_name: str
    pages: str
    chunk_text: str


@router.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload un fichier, le traite et stocke ses chunks dans ChromaDB.
    """
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Sauvegarde temporaire du fichier
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Traitement et stockage dans ChromaDB
    stored_chunks = store_document_chunks(file_path) # la fonction qui sort les chunks du fichier

    return {"message": "Document ajouté", "chunks": stored_chunks}

@router.post("/add_document/")
def add_document(chunk: DocumentChunk):
    """Endpoint pour ajouter un chunk de document dans ChromaDB."""
    metadata = add_document_chunk(chunk.file_name, chunk.pages, chunk.chunk_text)
    return metadata

@router.get("/all_documents/")
def all_documents():
    """Endpoint pour récupérer tous les documents dans ChromaDB."""
    results = get_all_documents()
    return {"results": results}

@router.delete("/delete_all_documents/")
def delete_all_documents():
    """
    Endpoint pour supprimer tous les documents de la collection ChromaDB.
    """
    from app.services.chroma_service import delete_all_documents_in_collection
    delete_all_documents_in_collection()
    return {"message": "Tous les documents ont été supprimés de la collection."}


@router.get("/search/")
def search(query: str = None):
    """Endpoint pour rechercher un document dans ChromaDB."""
    results = search_documents(query)
    return {"results": results}

@router.get("/search_ranking/")
def search_ranking(query: str = None):
    """Endpoint pour rechercher un document dans ChromaDB."""
    results = search_documents_ranking(query)
    return {"results": results}