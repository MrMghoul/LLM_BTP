from app.core.database import database
from app.core.config import MONGO_COLLECTION_NAME
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Récupérer la collection "documents"
collection = database[MONGO_COLLECTION_NAME]

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
