from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chroma_service import search_documents
from app.services.llm_service import ask_question, generate_response

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    history: str  # Ajouter l'historique des messages

@router.post("/chat/")
async def chat(request: QueryRequest):
    """
    Endpoint pour interroger le LLM avec une question et obtenir une réponse.
    """
    query = request.query
    history = request.history
    
    # Rechercher les documents dans ChromaDB
    documents = search_documents(query)
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for the query.")
    
    # Générer une réponse à partir du LLM en utilisant les documents trouvés
    response = generate_response(query, documents, history)  # Passer l'historique des messages
    
    return {"query": query, "response": response}

@router.post("/ask/")
async def ask(request: QueryRequest):
    """
    Endpoint pour poser une question directement au LLM et obtenir une réponse.
    """
    query = request.query
    history = request.history
    
    # Poser la question au LLM
    response = await ask_question(query, history)  # Utilisez await ici et passez l'historique
    
    return {"question": query, "response": response}