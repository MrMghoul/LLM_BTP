from app.core.database import database
from app.core.config import MONGO_COLLECTION_NAME
from bson import ObjectId

# Récupérer la collection "documents"
collection = database[MONGO_COLLECTION_NAME]


async def get_all_documents():
    """Récupère tous les documents de la collection."""
    documents = await collection.find().to_list(100)  # Limité à 100 documents
    return [{"id": str(doc["_id"]), "name": doc["name"]} for doc in documents]

