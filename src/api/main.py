"""
Application FastAPI principale
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Créer l'application FastAPI
app = FastAPI(
    title=os.getenv('APP_NAME', 'ENSA Chatbot'),
    version=os.getenv('APP_VERSION', '1.0.0'),
    description="Chatbot intelligent pour l'ENSA El Jadida avec RAG et agents",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
origins = eval(os.getenv('CORS_ORIGINS', '["*"]'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importer les routes
from .routes import chat_router, documents_router, health_router

# Enregistrer les routes
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])

@app.on_event("startup")
async def startup_event():
    """Événement au démarrage"""
    print("=" * 60)
    print(f"🚀 {os.getenv('APP_NAME')} v{os.getenv('APP_VERSION')}")
    print(f"🔗 Ollama: {os.getenv('OLLAMA_BASE_URL')}")
    print(f"🤖 Modèle: {os.getenv('OLLAMA_MODEL')}")
    print(f"📊 Embeddings: {os.getenv('OLLAMA_EMBEDDING_MODEL')}")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt"""
    print("\n👋 ENSA Chatbot arrêté")

@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "Bienvenue sur ENSA Chatbot API",
        "version": os.getenv('APP_VERSION'),
        "docs": "/docs",
        "health": "/api/health"
    }