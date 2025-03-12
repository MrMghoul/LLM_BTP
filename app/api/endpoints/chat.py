import os
import shutil
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from app.services.chroma_service import search_documents
from app.services.llm_service import ask_question, generate_response
from app.utils.file_processing import process_file
from app.services.chroma_service import store_document_chunks
from fastapi import Form

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    history: str

@router.post("/chat/")
async def chat(query: str = Form(...), history: str = Form(...), file: UploadFile = File(None)):
    """
    Endpoint pour interroger le LLM avec une question et obtenir une réponse.
    """
    # Rechercher les documents dans ChromaDB
    documents = search_documents(query)
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for the query.")
    
    # Traiter le fichier s'il est fourni
    folder_chunks = []
    if file:
        UPLOAD_FOLDER = "uploads"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Utiliser store_document_chunks pour obtenir les chunks
        chunks = store_document_chunks(file_path)
        
        # Filtrer les informations pour ne conserver que le nom du fichier et les chunks
        folder_chunks = [{"file_name": chunk["file_name"], "chunk": chunk["chunk"]} for chunk in chunks]
    
    # Générer une réponse à partir du LLM
    response = await generate_response(query, documents, history, folder_chunks)
    
    return {"query": query, "response": response}

@router.post("/ask/")
async def ask(request: QueryRequest):
    """
    Endpoint pour poser une question directement au LLM et obtenir une réponse.
    """
    query = request.query
    
    # Poser la question au LLM
    response = await ask_question(query)
    
    return {"question": query, "response": response}