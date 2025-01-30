from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, MONGO_DB_NAME

# Initialiser la connexion MongoDB
client = AsyncIOMotorClient(MONGO_URI)
database = client[MONGO_DB_NAME]
