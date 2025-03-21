from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

# Charger le tokenizer et le modèle en mode CPU-friendly
model_name = "microsoft/phi-2"  # Ou "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,  # float32 pour CPU
    device_map="cpu"  # Forcer l'utilisation du CPU
)

async def generate_response(query: str) -> str:
    """
    Génère une réponse naturelle à partir de la question.
    """
    inputs = tokenizer(query, return_tensors="pt").to("cpu")
    
    # Utilisation de la génération par échantillonnage
    outputs = model.generate(
        **inputs, 
        max_length=50,  # Limiter la longueur de la réponse
        temperature=0.7,  # Température pour la diversité
        top_p=0.9,  # Utilisation du top-p pour plus de variété
        do_sample=True,  # Permet l'échantillonnage pour générer des réponses variées
        pad_token_id=tokenizer.eos_token_id  # Utiliser le token de fin comme token de padding
    )
    
    # Décoder la réponse générée
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response

@router.post("/chat/")
async def chat(request: QueryRequest):
    """
    Endpoint pour poser une question au modèle et obtenir une réponse.
    """
    query = request.query
    response = await generate_response(query)

    return {"response": response}
