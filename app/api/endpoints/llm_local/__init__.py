from fastapi import APIRouter
from .deepseek_endpoint import router as deepseek_router
from .gpt2_endpoint import router as gpt2_router
from .deepseek_moe_endpoint import router as deepseek_moe_router

router = APIRouter()
router.include_router(deepseek_router, prefix="/deepseek", tags=["DeepSeek-R1-Distill-Qwen-1.5B"])
router.include_router(gpt2_router, prefix="/gpt2", tags=["GPT-2"])
router.include_router(deepseek_moe_router, prefix="/deepseek_moe", tags=["microsoft/phi-2"])