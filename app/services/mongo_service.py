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
    return [{"id": str(doc["_id"]), "name": doc["name"]} for doc in documents]

def insert_chunks_to_mongodb(chunks, collection_name):
    """
    Insère les chunks de texte dans une collection MongoDB.

    :param chunks: Liste de chunks de texte à insérer.
    :param collection_name: Nom de la collection MongoDB.
    """
    try:
        collection = database[collection_name]
        collection.insert_many(chunks)
        logger.info(f"Inserted {len(chunks)} chunks into MongoDB collection '{collection_name}'")
    except Exception as e:
        logger.error(f"Error inserting chunks into MongoDB: {e}")
        raise

def convert_objectid_to_str(data):
    """
    Convertit les ObjectId en chaînes de caractères dans un dictionnaire ou une liste de dictionnaires.
    
    :param data: Le dictionnaire ou la liste de dictionnaires à convertir.
    :return: Le dictionnaire ou la liste de dictionnaires avec les ObjectId convertis en chaînes de caractères.
    """
    if isinstance(data, list):
        for item in data:
            convert_objectid_to_str(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                convert_objectid_to_str(value)
    return data