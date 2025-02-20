from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Définition du chemin de stockage de la base ChromaDB
CHROMA_PATH = "./chroma_db"

# Chargement du modèle d'embedding
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialisation de la base de données vectorielle
chroma_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_model)
