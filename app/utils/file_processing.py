from docx import Document
import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

def divide_text_by_min_words(text, min_words=100):
    """
    Divise le texte en morceaux contenant au moins un nombre minimum de mots.
    
    :param text: Le texte à diviser.
    :param min_words: Le nombre minimum de mots par chunk.
    :return: Une liste de morceaux de texte.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= min_words:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    # Ajouter le dernier chunk s'il contient des mots
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def process_word_file(file_path):
    """
    Traite un fichier Word et le divise en morceaux de texte basés sur les paragraphes.
    Détecte également les images et les inclut dans les chunks.
    
    :param file_path: Le chemin du fichier Word.
    :return: Une liste de morceaux de texte avec des informations sur le fichier et les pages.
    """
    try:
        doc = Document(file_path)
        full_text = []
        current_page = 1
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # Détecter les images
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                full_text.append(f"[Image: {rel.target_ref}]")
        
        text = ' '.join(full_text)
        chunks = divide_text_by_min_words(text)
        return [{"file_name": file_path, "pages": f"{current_page}", "chunk": chunk} for chunk in chunks]
    except Exception as e:
        logger.error(f"Error processing Word file: {e}")
        raise

def process_pdf_file(file_path):
    """
    Traite un fichier PDF et le divise en morceaux de texte basés sur les paragraphes.
    
    :param file_path: Le chemin du fichier PDF.
    :return: Une liste de morceaux de texte avec des informations sur le fichier et les pages.
    """
    doc = fitz.open(file_path)
    full_text = []
    current_page = 1
    current_chunk = []
    chunks = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        words = text.split()
        
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= 100:
                chunks.append({
                    "file_name": file_path,
                    "pages": f"{current_page}-{page_num}" if current_page != page_num else str(page_num),
                    "chunk": ' '.join(current_chunk)
                })
                current_chunk = []
                current_page = page_num

    # Ajouter le dernier chunk s'il contient des mots
    if current_chunk:
        chunks.append({
            "file_name": file_path,
            "pages": f"{current_page}-{page_num}" if current_page != page_num else str(page_num),
            "chunk": ' '.join(current_chunk)
        })

    return chunks