from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

# Charger le tokenizer et le modèle
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

async def generate_deepseek_response(query: str) -> str:
    """
    Génère une réponse à partir de DeepSeek-R1.5B.
    """
    inputs = tokenizer(query, return_tensors="pt")
    outputs = model.generate(inputs.input_ids, max_length=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response

@router.post("/deepseek/")
async def deepseek(request: QueryRequest):
    """
    Endpoint pour poser une question à DeepSeek-R1-Distill-Qwen-1.5B et obtenir une réponse.
    """
    query = request.query
    
    # Poser la question à DeepSeek-R1-Distill-Qwen-1.5B
    response = await generate_deepseek_response(query)
    
    return {"question": query, "response": response}