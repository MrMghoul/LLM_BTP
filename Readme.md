Installation environnement :

dans le LLM_projet : 
    python -m venv envllm 
    envllm\Scripts\activate
    pip install -r requirements.txt

lancer le Backend : 
    uvicorn app.main:app --reload

swagger : 
    http://127.0.0.1:8000/docs