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

@router.post("/upload_folder/")
async def upload_folder(folder_path: str):
    """
    Upload tous les fichiers d'un dossier, les traite et stocke leurs chunks dans ChromaDB.
    """
    if not os.path.isdir(folder_path):
        return {"error": "Le chemin spécifié n'est pas un dossier valide."}

    processed_files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Vérifier si c'est un fichier
        if os.path.isfile(file_path):
            try:
                # Traiter le fichier et stocker les chunks dans ChromaDB
                chunks = process_file(file_path)
                store_document_chunks(file_path)  # Stockage des chunks dans ChromaDB
                processed_files.append({"file_name": file_name, "status": "success", "chunks": chunks})
            except Exception as e:
                processed_files.append({"file_name": file_name, "status": "error", "message": str(e)})

    return {"message": "Traitement terminé", "processed_files": processed_files}

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