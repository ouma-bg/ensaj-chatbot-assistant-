"""
Script pour lancer l'API
"""

import os
import uvicorn
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser le système RAG avant de lancer l'API
from src.rag import (
    OllamaEmbeddings,
    DocumentLoader,
    TextSplitter,
    FAISSVectorStore,
    Retriever
)
from src.api.routes import initialize_rag_system

def setup_rag():
    """Configurer le système RAG"""
    print("\n🔧 Configuration du système RAG...")
    
    # Embeddings
    embeddings = OllamaEmbeddings()
    
    # Vector store
    vector_store = FAISSVectorStore(embeddings)
    
    # Vérifier si un index existe
    index_path = os.getenv('VECTOR_DB_PATH', './data/embeddings/faiss_index')
    
    if os.path.exists(os.path.join(index_path, 'index.faiss')):
        print("📂 Chargement de l'index existant...")
        vector_store.load(index_path)
    else:
        print("⚠️ Aucun index trouvé. Ajoutez des documents avec 'python scripts/index_documents.py'")
    
    # Retriever
    retriever = Retriever(vector_store)
    
    # Initialiser dans l'API
    initialize_rag_system(vector_store, retriever)
    
    print("✅ Système RAG prêt!\n")
    return vector_store, retriever

if __name__ == "__main__":
    # Setup RAG
    setup_rag()
    
    # Configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8080))
    reload = os.getenv('API_RELOAD', 'True').lower() == 'true'
    
    # Lancer l'API
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload
    )
