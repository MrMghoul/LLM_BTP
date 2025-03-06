import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chroma_service import search_documents
from app.services.llm_service import ask_question, generate_response

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat/")
async def chat(request: QueryRequest):
    """
    Endpoint pour interroger le LLM avec une question et obtenir une réponse.
    """
    query = request.query
    
    # Rechercher les documents dans ChromaDB
    documents = search_documents(query)
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for the query.")
    
    # Générer une réponse à partir du LLM
    response = generate_response(query, documents)
    
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