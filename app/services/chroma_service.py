from datetime import datetime
from app.core.chroma_config import chroma_db, embedding_model
from app.utils.file_processing import process_file
from langchain_community.vectorstores.utils import filter_complex_metadata


def store_document_chunks(file_path: str):
    """
    Traite un document, extrait ses chunks et les stocke dans ChromaDB.
    
    :param file_path: Chemin du fichier à traiter.
    :return: Liste des documents insérés dans la base.
    """
    # Obtenir les chunks du document
    chunks = process_file(file_path)
    if isinstance(chunks, dict) and chunks.get("status") == "error":
        raise ValueError(chunks["message"])


    # Ajouter les chunks à ChromaDB
    for chunk in chunks:
        metadata = {
            "file_name": chunk["file_name"],
            "pages": chunk["pages"],
            "timestamp": chunk["timestamp"],
            "chunk": chunk["chunk"],
            #"vector": chunk["vector"]  # On stocke aussi le vecteur
        }
        
        chroma_db.add_texts(texts=[chunk["chunk"]], metadatas=[metadata], vectors=[chunk["vector"]])

    chroma_db.persist()  # Sauvegarde des changements

    return chunks  # Retourne les données stockées

def add_document_chunk(file_name: str, page: str, chunk_text: str):
    """Ajoute un chunk de document dans ChromaDB."""
    
    timestamp = str(datetime.now())
    vector = embedding_model.embed_query(chunk_text)
    metadata = {
        "file_name": file_name,
        "pages": page,
        "timestamp": timestamp,
        "chunk": chunk_text,
        #"vector": vector
    }
    chroma_db.add_texts(texts=[chunk_text], metadatas=[metadata], vectors=[vector])
    chroma_db.persist()

def search_documents(query: str = None, top_k: int = 3):
    """Affiche tous les documents dans ChromaDB."""
    if query:
        results = chroma_db.similarity_search(query, k=top_k)
    else:
        results = chroma_db.get_all_documents()
    
    return [{"file_name": doc.metadata["file_name"], 
             "page": doc.metadata["pages"],
             "timestamp": doc.metadata["timestamp"],
             "content": doc.page_content} for doc in results]