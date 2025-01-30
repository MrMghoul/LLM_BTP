from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "llm_project")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "documents")
