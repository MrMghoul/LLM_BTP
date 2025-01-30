from fastapi import FastAPI
from app.api.router import router  # Importer le routeur principal

app = FastAPI()

# Inclure le routeur dans l'application FastAPI
app.include_router(router)
