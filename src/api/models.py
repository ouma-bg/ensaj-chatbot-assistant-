"""
Modèles Pydantic pour l'API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    """Requête de chat"""
    message: str = Field(..., description="Question de l'utilisateur")
    conversation_id: Optional[str] = Field(None, description="ID de conversation")
    use_rag: bool = Field(True, description="Utiliser RAG ou non")
    stream: bool = Field(False, description="Réponse en streaming")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Quels sont les conditions d'admission à l'ENSA?",
                "use_rag": True,
                "stream": False
            }
        }

class ChatResponse(BaseModel):
    """Réponse du chatbot"""
    response: str = Field(..., description="Réponse générée")
    conversation_id: str = Field(..., description="ID de conversation")
    sources: Optional[List[Dict]] = Field(None, description="Sources utilisées")
    processing_time: float = Field(..., description="Temps de traitement (secondes)")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Les conditions d'admission à l'ENSA incluent...",
                "conversation_id": "conv_123456",
                "sources": [
                    {
                        "source": "reglement.pdf",
                        "page": 3,
                        "score": 0.89
                    }
                ],
                "processing_time": 2.34,
                "timestamp": "2024-01-15T10:30:00"
            }
        }

class DocumentInfo(BaseModel):
    """Information sur un document"""
    filename: str
    size: int
    type: str
    chunks: int
    uploaded_at: datetime

class DocumentUploadResponse(BaseModel):
    """Réponse après upload de document"""
    success: bool
    message: str
    document: Optional[DocumentInfo] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Document chargé avec succès",
                "document": {
                    "filename": "nouveau_reglement.pdf",
                    "size": 245760,
                    "type": "pdf",
                    "chunks": 15,
                    "uploaded_at": "2024-01-15T10:30:00"
                }
            }
        }

class HealthResponse(BaseModel):
    """Statut de santé de l'API"""
    status: str
    version: str
    ollama_connected: bool
    vector_store_loaded: bool
    total_documents: int
    timestamp: datetime = Field(default_factory=datetime.now)