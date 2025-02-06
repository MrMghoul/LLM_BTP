import re
import spacy
import fitz  # PyMuPDF
import docx
import os

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")  # Recharger le modèle après l'installation

def is_noise(text):
    """Détecte si le texte est du bruit (listes de petits points, etc.)."""
    return bool(re.search(r'\.{3,}', text)) or bool(re.search(r'(\.{2,}|\-{2,}|\_{2,})', text))

def extract_page_numbers(doc):
    """Extrait les numéros de page des pieds de page du document."""
    page_numbers = {}
    for section in doc.sections:
        footer = section.footer
        for para in footer.paragraphs:
            text = para.text.strip()
            if text.isdigit():
                page_numbers[int(text)] = int(text)
    return page_numbers


def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un PDF et tente d'identifier les titres et sous-titres."""
    doc = fitz.open(pdf_path)
    chunks = []
    current_chunk = []
    min_chunk_length = 70  # Longueur minimale d'un chunk
    
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")  # Récupère les blocs de texte
        for block in blocks:
            text = block[4].strip()
            if not text or is_noise(text):
                continue
            
            # Heuristique : si texte est en majuscules ou a une taille de police plus grande, c'est un titre
            if text.isupper() or len(text.split()) < 5:  
                if current_chunk:
                    chunks.append({"chunk": "\n".join(current_chunk), "file": os.path.basename(pdf_path), "page": page_num})
                    current_chunk = []
                chunks.append({"chunk": text, "file": os.path.basename(pdf_path), "page": page_num})  # Ajouter le titre directement
            else:
                current_chunk.append(text)

    if current_chunk:
        chunks.append({"chunk": "\n".join(current_chunk), "file": os.path.basename(pdf_path), "page": page_num})

    merged_chunks = []
    for i, chunk in enumerate(chunks):
        if merged_chunks and len(chunk["chunk"]) < min_chunk_length:
            merged_chunks[-1]["chunk"] += " " + chunk["chunk"]
        elif i == 0 and len(chunk["chunk"]) < min_chunk_length and len(chunks) > 1:
            # Si le premier chunk est trop petit, le fusionner avec le suivant
            chunks[1]["chunk"] = chunk["chunk"] + " " + chunks[1]["chunk"]
        else:
            merged_chunks.append(chunk)
    
    return merged_chunks


def extract_text_from_docx(docx_path):
    """Extrait le texte d'un fichier Word en séparant les titres et paragraphes."""
    doc = docx.Document(docx_path)
    chunks = []
    current_chunk = []
    min_chunk_length = 70  # Longueur minimale d'un chunk
    page_numbers = extract_page_numbers(doc)
    current_page = 1
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text or is_noise(text):
            continue
        
        # Détection des titres (heuristique : styles "Heading 1", "Heading 2" etc.)
        if para.style.name.startswith("Heading"):
            if current_chunk:
                chunks.append({"chunk": "\n".join(current_chunk), "file": os.path.basename(docx_path), "page": current_page})
                current_chunk = []
            chunks.append({"chunk": text, "file": os.path.basename(docx_path), "page": current_page})  # Ajouter le titre
        else:
            current_chunk.append(text)
        
        # Mettre à jour le numéro de page si le paragraphe contient un saut de page
        if para.runs and any(run.text == '\f' for run in para.runs):
            current_page += 1
        
        # Mettre à jour le numéro de page en fonction des numéros de page extraits
        for page_num in page_numbers:
            if page_num > current_page:
                current_page = page_num
                break

    if current_chunk:
        chunks.append({"chunk": "\n".join(current_chunk), "file": os.path.basename(docx_path), "page": current_page})

    merged_chunks = []
    for i, chunk in enumerate(chunks):
        if merged_chunks and len(chunk["chunk"]) < min_chunk_length:
            merged_chunks[-1]["chunk"] += " " + chunk["chunk"]
        elif i == 0 and len(chunk["chunk"]) < min_chunk_length and len(chunks) > 1:
            # Si le premier chunk est trop petit, le fusionner avec le suivant
            chunks[1]["chunk"] = chunk["chunk"] + " " + chunks[1]["chunk"]
        else:
            merged_chunks.append(chunk)
    
    return merged_chunks


def process_file(file_path):
    """Détecte le type de fichier et applique l'extraction correspondante."""
    _, ext = os.path.splitext(file_path)
    if ext.lower() == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext.lower() == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Format non supporté !")