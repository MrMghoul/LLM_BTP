from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router  # Importer le routeur principal

app = FastAPI()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Autoriser votre frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure le routeur dans l'application FastAPI
app.include_router(router)