# filepath: c:\Users\Skyzo\Desktop\Projet probtp\LLM_BTP\app\api\router.py
from fastapi import APIRouter
from app.api.endpoints import document, chroma, chat, conversations, gpt2

router = APIRouter()
router.include_router(document.router, prefix="/api", tags=["documents"])
router.include_router(chroma.router, prefix="/api", tags=["chroma"])
router.include_router(chat.router, prefix="/api", tags=["chat"])
router.include_router(conversations.router, prefix="/api", tags=["conversations"])
router.include_router(gpt2.router, prefix="/api", tags=["gpt2"])
