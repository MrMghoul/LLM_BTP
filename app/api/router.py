from fastapi import APIRouter
from app.api.endpoints import document, chroma, chat, conversations

router = APIRouter()
router.include_router(document.router, prefix="/api", tags=["documents"])
router.include_router(chroma.router, prefix="/api", tags=["chroma"])
router.include_router(chat.router, prefix="/api", tags=["chat"])
router.include_router(conversations.router, prefix="/api", tags=["conversations"])