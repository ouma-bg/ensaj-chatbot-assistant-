import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

class OllamaEmbeddings:
    """Génère des embeddings avec Ollama"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        print(f"🔌 Embeddings: {self.model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Générer embeddings pour plusieurs documents"""
        embeddings = []
        total = len(texts)
        
        for i, text in enumerate(texts, 1):
            print(f"📊 Embedding {i}/{total}...", end='\r')
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        
        print(f"\n✅ {total} embeddings générés")
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Générer embedding pour une requête"""
        return self._get_embedding(text)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Appel API Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text[:2000]  # Limite pour éviter erreurs
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"\n❌ Erreur embedding: {e}")
            raise