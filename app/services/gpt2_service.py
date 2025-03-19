# filepath: c:\Users\Skyzo\Desktop\Projet probtp\LLM_BTP\app\services\gpt2_service.py
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Charger le modèle et le tokenizer GPT-2
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

def generate_gpt2_response(prompt: str, max_length: int = 100):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response