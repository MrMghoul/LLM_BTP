# filepath: c:\Users\Skyzo\Desktop\Projet probtp\LLM_BTP\app\api\endpoints\gpt2.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gpt2_service import generate_gpt2_response

router = APIRouter()

class GPT2Request(BaseModel):
    prompt: str
    max_length: int = 100

@router.post("/gpt2/")
async def gpt2(request: GPT2Request):
    """
    Endpoint pour interroger le modèle GPT-2 avec un prompt et obtenir une réponse.
    """
    response = generate_gpt2_response(request.prompt, request.max_length)
    return {"prompt": request.prompt, "response": response}