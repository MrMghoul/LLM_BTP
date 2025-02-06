from fastapi import APIRouter
from app.api.endpoints import document

router = APIRouter()
router.include_router(document.router, prefix="/api", tags=["documents"])