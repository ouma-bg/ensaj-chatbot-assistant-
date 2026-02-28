"""
Routes de l'API
"""

import os
import time
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime
import requests
from dotenv import load_dotenv

from .models import (
    ChatRequest, 
    ChatResponse, 
    DocumentUploadResponse, 
    DocumentInfo,
    HealthResponse
)

load_dotenv()

# Routers
health_router = APIRouter()
chat_router = APIRouter()
documents_router = APIRouter()

# Variables globales (à remplacer par un vrai système de gestion d'état)
vector_store = None
retriever = None
conversation_history = {}

# ==========================================
# HEALTH CHECK
# ==========================================

@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifier l'état de santé de l'API"""
    
    # Vérifier connexion Ollama
    ollama_connected = False
    try:
        response = requests.get(
            f"{os.getenv('OLLAMA_BASE_URL')}/api/tags",
            timeout=5
        )
        ollama_connected = response.status_code == 200
    except:
        pass
    
    # Vérifier vector store
    vector_store_loaded = vector_store is not None and len(vector_store.documents) > 0
    total_docs = len(vector_store.documents) if vector_store else 0
    
    return HealthResponse(
        status="healthy" if ollama_connected and vector_store_loaded else "degraded",
        version=os.getenv('APP_VERSION', '1.0.0'),
        ollama_connected=ollama_connected,
        vector_store_loaded=vector_store_loaded,
        total_documents=total_docs
    )

# ==========================================
# CHAT
# ==========================================

@chat_router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat
    """
    start_time = time.time()
    
    # Générer ID de conversation si absent
    conv_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
    
    try:
        # Récupérer le contexte via RAG si activé
        context = ""
        sources = []
        
        if request.use_rag and retriever:
            results = retriever.retrieve(request.message)
            context = retriever.format_context(results)
            
            # Extraire les sources
            for doc, score in results:
                sources.append({
                    "source": doc.metadata.get('source', 'Unknown'),
                    "page": doc.metadata.get('page'),
                    "score": round(score, 2)
                })
        
        # Construire le prompt
        prompt = _build_prompt(request.message, context, conv_id)
        
        # Appeler Ollama
        response_text = await _call_ollama(prompt, request.stream)
        
        # Calculer temps de traitement
        processing_time = round(time.time() - start_time, 2)
        
        # Sauvegarder dans l'historique
        if conv_id not in conversation_history:
            conversation_history[conv_id] = []
        
        conversation_history[conv_id].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now()
        })
        conversation_history[conv_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now()
        })
        
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            sources=sources if sources else None,
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

def _build_prompt(message: str, context: str, conv_id: str) -> str:
    """Construire le prompt avec contexte"""
    
    # Récupérer l'historique
    history = conversation_history.get(conv_id, [])
    history_text = ""
    
    if history:
        for msg in history[-4:]:  # Garder seulement les 4 derniers messages
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n\n"
    
    # Template du prompt
    system_prompt = """Tu es un assistant virtuel pour l'ENSA (École Nationale des Sciences Appliquées) El Jadida.

Ton rôle:
- Répondre aux questions des étudiants (actuels et futurs) sur l'ENSA
- Fournir des informations précises basées sur les documents fournis
- Être poli, professionnel et encourageant
- Répondre en français ou en arabe selon la langue de la question

Si tu ne connais pas la réponse, dis-le honnêtement et suggère de contacter l'administration."""

    if context:
        prompt = f"""{system_prompt}

CONTEXTE (Documents de l'ENSA):
{context}

{"HISTORIQUE:" if history_text else ""}
{history_text}

QUESTION ACTUELLE:
{message}

RÉPONSE:"""
    else:
        prompt = f"""{system_prompt}

{"HISTORIQUE:" if history_text else ""}
{history_text}

QUESTION:
{message}

RÉPONSE:"""
    
    return prompt

async def _call_ollama(prompt: str, stream: bool = False) -> str:
    """Appeler Ollama pour générer une réponse"""
    try:
        response = requests.post(
            f"{os.getenv('OLLAMA_BASE_URL')}/api/generate",
            json={
                "model": os.getenv('OLLAMA_MODEL'),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": float(os.getenv('TEMPERATURE', 0.7)),
                    "num_predict": int(os.getenv('MAX_TOKENS', 2048))
                }
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Ollama: {str(e)}")

# ==========================================
# DOCUMENTS
# ==========================================

@documents_router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload un nouveau document
    """
    try:
        # Vérifier le type de fichier
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400, 
                detail="Type de fichier non supporté. Utilisez PDF ou TXT."
            )
        
        # Sauvegarder le fichier
        file_path = os.path.join("data/raw", file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # TODO: Traiter le document et l'ajouter au vector store
        # Pour l'instant, on retourne juste une confirmation
        
        return DocumentUploadResponse(
            success=True,
            message=f"Document '{file.filename}' uploadé avec succès",
            document=DocumentInfo(
                filename=file.filename,
                size=len(content),
                type=file.filename.split('.')[-1],
                chunks=0,  # À calculer après traitement
                uploaded_at=datetime.now()
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur upload: {str(e)}")

@documents_router.get("/list")
async def list_documents():
    """
    Lister tous les documents chargés
    """
    if not vector_store or not vector_store.documents:
        return {"documents": [], "total": 0}
    
    # Extraire infos uniques des documents
    docs_info = {}
    for doc in vector_store.documents:
        source = doc.metadata.get('source', 'Unknown')
        if source not in docs_info:
            docs_info[source] = {
                "source": source,
                "type": doc.metadata.get('type', 'unknown'),
                "chunks": 0
            }
        docs_info[source]["chunks"] += 1
    
    return {
        "documents": list(docs_info.values()),
        "total": len(docs_info)
    }

@documents_router.delete("/{filename}")
async def delete_document(filename: str):
    """
    Supprimer un document
    """
    # TODO: Implémenter la suppression du vector store
    return {
        "success": False,
        "message": "Fonction non implémentée"
    }

# ==========================================
# INITIALISATION
# ==========================================

def initialize_rag_system(vs, ret):
    """
    Initialiser le système RAG (appelé depuis main.py)
    """
    global vector_store, retriever
    vector_store = vs
    retriever = ret
    print("✅ Système RAG initialisé dans l'API")