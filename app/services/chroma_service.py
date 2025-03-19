from datetime import datetime
from app.core.chroma_config import chroma_db, embedding_model
from app.utils.file_processing import process_file
from langchain_community.vectorstores.utils import filter_complex_metadata
from transformers import BertTokenizer, BertForSequenceClassification
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
model.eval()


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
model.eval()

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
        # Vérifier si le chunk existe déjà dans la base de données
        
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


def get_all_documents():
    """Récupère tous les documents dans ChromaDB."""
    results = chroma_db.similarity_search("", k=1000)  # Utiliser une recherche avec une chaîne vide pour récupérer tous les documents
    return [{"file_name": doc.metadata["file_name"], 
             "page": doc.metadata["pages"],
             "timestamp": doc.metadata["timestamp"],
             "content": doc.page_content} for doc in results]

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

def search_documents(query: str = None, top_k: int = 4):
    """Affiche tous les documents dans ChromaDB."""
    if query:
        results = chroma_db.similarity_search(query, k=top_k)
    else:
        results = chroma_db.get_all_documents()
    
    return [{"file_name": doc.metadata["file_name"], 
             "page": doc.metadata["pages"],
             "timestamp": doc.metadata["timestamp"],
             "content": doc.page_content} for doc in results]
    
def rank_chunks(query, chunks):
    """
    Utilise BERT pour classer les chunks en fonction de la pertinence par rapport à la requête.
    
    :param query: La requête de recherche.
    :param chunks: Les chunks de texte à classer.
    :return: Les chunks classés par pertinence.
    """
    inputs = tokenizer([query] * len(chunks), chunks, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits[:, 1]  # Supposons que le modèle de classification binaire donne des scores de pertinence
    ranked_chunks = [chunk for _, chunk in sorted(zip(scores, chunks), key=lambda pair: pair[0], reverse=True)]
    return ranked_chunks


def search_documents_ranking(query: str = None, top_k: int = 4):
    """Recherche des documents dans ChromaDB et les classe en utilisant BERT."""
    if query:
        results = chroma_db.similarity_search(query, k=top_k)
    else:
        results = chroma_db.get_all_documents()
    
    chunks = [{"file_name": doc.metadata["file_name"], 
               "page": doc.metadata["pages"],
               "timestamp": doc.metadata["timestamp"],
               "content": doc.page_content} for doc in results]
    
    if query:
        ranked_chunks = rank_chunks(query, [chunk["content"] for chunk in chunks])
        for i, chunk in enumerate(ranked_chunks):
            chunks[i]["content"] = chunk
    
    return chunks[:top_k]