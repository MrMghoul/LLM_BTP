from fastapi import APIRouter, HTTPException, UploadFile, File
from app.utils.file_processing import process_word_file, process_pdf_file, process_doc_file
import os
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/process-file/")
async def process_file(file: UploadFile = File(...)):
    """Divise le fichier en chunks de texte basés sur les paragraphes."""
    logger.info(f"Received file: {file.filename} with content type: {file.content_type}")
    try:
        file_path = os.path.abspath(f"test/{file.filename}")
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            chunks = process_word_file(file_path)
        elif file.content_type == "application/pdf":
            chunks = process_pdf_file(file_path)
        elif file.content_type == "application/msword":
            chunks = process_doc_file(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        logger.info(f"Processed file: {file.filename}, number of chunks: {len(chunks)}")
        os.remove(file_path)
        
        return {"chunks": chunks}
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))