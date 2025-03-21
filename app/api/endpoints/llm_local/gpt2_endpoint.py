from fastapi import APIRouter
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer

router = APIRouter()

class GPT2Request(BaseModel):
    prompt: str
    max_length: int = 100

# Charger le tokenizer et le modèle GPT-2
gpt2_model_name = "gpt2"
gpt2_tokenizer = GPT2Tokenizer.from_pretrained(gpt2_model_name)
gpt2_model = GPT2LMHeadModel.from_pretrained(gpt2_model_name)

def generate_gpt2_response(prompt: str, max_length: int = 100) -> str:
    """
    Génère une réponse à partir de GPT-2.
    """
    inputs = gpt2_tokenizer(prompt, return_tensors="pt")
    outputs = gpt2_model.generate(inputs.input_ids, max_length=max_length)
    response = gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response

@router.post("/gpt2/")
async def gpt2(request: GPT2Request):
    """
    Endpoint pour interroger le modèle GPT-2 avec un prompt et obtenir une réponse.
    """
    response = generate_gpt2_response(request.prompt, request.max_length)
    return {"prompt": request.prompt, "response": response}