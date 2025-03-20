from app.core.database import database
from app.core.config import MONGO_COLLECTION_NAME
from bson import ObjectId


# Récupérer la collection "documents"
collection = database[MONGO_COLLECTION_NAME]
conversation_collection = database["conversations"]

async def get_all_documents():
    """Récupère tous les documents de la collection."""
    documents = await collection.find().to_list(100)  # Limité à 100 documents
    for doc in documents:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return documents

async def insert_document(document):
    """Insère un document dans la collection."""
    result = await collection.insert_one(document)
    return str(result.inserted_id)

# Fonctions pour gérer les conversations
conversation_collection = database["conversations"]

async def get_all_conversations():
    """Récupère toutes les conversations."""
    conversations = await conversation_collection.find().to_list(100)
    for conv in conversations:
        conv["id"] = str(conv["_id"])
        del conv["_id"]
    return conversations

async def insert_conversation(conversation):
    """Insère une conversation dans la collection."""
    result = await conversation_collection.insert_one(conversation)
    return str(result.inserted_id)

async def update_conversation(conversation_id, conversation):
    """Met à jour une conversation dans la collection."""
    result = await conversation_collection.update_one({"_id": ObjectId(conversation_id)}, {"$set": conversation})
    return result.modified_count

async def delete_conversation(conversation_id):
    """Supprime une conversation de la collection."""
    result = await conversation_collection.delete_one({"_id": ObjectId(conversation_id)})
    return result.deleted_count 

async def find_conversation_by_history(history: str):
    """
    Recherche une conversation existante en fonction de la requête.
    
    :param query: La requête de l'utilisateur.
    :return: La conversation trouvée ou None.
    """
    conversation = await conversation_collection.find_one({"Messages": history})
    return conversation

async def update_uploaded_chunks(conversation_id, new_chunks):
    """
    Met à jour les chunks uploadés dans une conversation.
    
    :param conversation_id: ID de la conversation.
    :param new_chunks: Liste des nouveaux chunks à ajouter.
    :return: Nombre de documents modifiés.
    """
    conversation = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
    if not conversation:
        raise ValueError("Conversation introuvable.")

    # Récupérer les chunks existants et ajouter les nouveaux
    existing_chunks = conversation.get("uploaded_chunks", [])
    updated_chunks = existing_chunks + new_chunks

    result = await conversation_collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"uploaded_chunks": updated_chunks}}
    )
    return result.modified_count


async def get_uploaded_chunks(conversation_id):
    """
    Récupère les chunks uploadés pour une conversation.
    
    :param conversation_id: ID de la conversation.
    :return: Liste des chunks uploadés.
    """
    conversation = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
    if not conversation:
        raise ValueError("Conversation introuvable.")
    return conversation.get("uploaded_chunks", [])