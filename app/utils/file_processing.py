from docx import Document
import fitz  # PyMuPDF
import logging
import re
import os
import win32com.client as win32

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

def filter_unnecessary_sequences(text):
    """
    Filtre les séquences inutiles du texte.
    
    :param text: Le texte à filtrer.
    :return: Le texte filtré.
    """
    # Exemple de filtre pour les séquences de points
    text = re.sub(r'\.{3,}', '', text)
    return text

def process_word_file(file_path):
    """
    Traite un fichier Word et le divise en morceaux de texte basés sur les paragraphes.
    Détecte également les images et les inclut dans les chunks.
    
    :param file_path: Le chemin du fichier Word.
    :return: Une liste de morceaux de texte avec des informations sur le fichier.
    """
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip() == "":
                continue
            full_text.append(para.text)
        
        # Détecter les images
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                full_text.append(f"[Image: {rel.target_ref}]")
        
        text = ' '.join(full_text)
        text = filter_unnecessary_sequences(text)
        chunks = divide_text_by_min_words(text)
        return [{"file_name": file_path, "chunk": chunk} for chunk in chunks]
    except Exception as e:
        logger.error(f"Error processing Word file: {e}")
        raise

def process_doc_file(file_path):
    """
    Traite un fichier Word .doc en le convertissant en .docx, puis le divise en morceaux de texte.
    
    :param file_path: Le chemin du fichier Word .doc.
    :return: Une liste de morceaux de texte avec des informations sur le fichier.
    """
    try:
        logger.info(f"Starting to process DOC file: {file_path}")
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Utiliser un chemin absolu
        abs_file_path = os.path.abspath(file_path)
        
        # Convertir le fichier .doc en .docx en utilisant pywin32
        word = win32.Dispatch("Word.Application")
        doc = word.Documents.Open(abs_file_path)
        docx_file_path = os.path.splitext(abs_file_path)[0] + '.docx'
        doc.SaveAs(docx_file_path, FileFormat=16)  # wdFormatXMLDocument = 16
        doc.Close()
        word.Quit()
        
        # Vérifier que le fichier .docx a été créé
        if not os.path.exists(docx_file_path):
            logger.error(f"Conversion failed, DOCX file not found: {docx_file_path}")
            raise FileNotFoundError(f"Conversion failed, DOCX file not found: {docx_file_path}")
        
        # Traiter le fichier .docx comme un fichier Word
        return process_word_file(docx_file_path)
    except Exception as e:
        logger.error(f"Error processing DOC file: {e}")
        raise

def process_pdf_file(file_path):
    """
    Traite un fichier PDF et le divise en morceaux de texte basés sur les paragraphes.
    
    :param file_path: Le chemin du fichier PDF.
    :return: Une liste de morceaux de texte avec des informations sur le fichier et les pages.
    """
    try:
        doc = fitz.open(file_path)
        full_text = []
        current_page = 1
        current_chunk = []
        chunks = []

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            text = filter_unnecessary_sequences(text)
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
    except Exception as e:
        logger.error(f"Error processing PDF file: {e}")
        raise