from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mongo_service import get_all_conversations, insert_conversation, update_conversation, delete_conversation

router = APIRouter()

class Conversation(BaseModel):
    query: str
    response: str
    messages: list

@router.get("/conversations/")
async def list_conversations():
    """Récupère toutes les conversations."""
    conversations = await get_all_conversations()
    return {"conversations": conversations}

@router.post("/conversations/")
async def add_conversation(conversation: Conversation):
    """Ajoute une nouvelle conversation."""
    conversation_id = await insert_conversation(conversation.dict())
    return {"id": conversation_id}

@router.put("/conversations/{conversation_id}")
async def update_conversation_endpoint(conversation_id: str, conversation: Conversation):
    """Met à jour une conversation."""
    await update_conversation(conversation_id, conversation.dict())
    return {"message": "Conversation mise à jour"}

@router.delete("/conversations/{conversation_id}")
async def remove_conversation(conversation_id: str):
    """Supprime une conversation."""
    await delete_conversation(conversation_id)
    return {"message": "Conversation supprimée"}