"""
Agent RAG pour le chatbot ENSA
Combine la récupération de documents avec la génération de réponses
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Dict, List, Optional
import yaml
import requests
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.rag.embeddings import OllamaEmbeddings

class RAGAgent:
    """Agent qui utilise RAG pour répondre aux questions"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialise l'agent RAG"""
        # Charger la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser les composants
        self.embedding_generator = OllamaEmbeddings(
    model_name=self.config.get('embeddings', {}).get('model')
)
        
        self.vector_store = VectorStore(
            persist_directory=self.config['chroma']['persist_directory'],
            collection_name=self.config['chroma']['collection_name'],
            embedding_generator=self.embedding_generator
        )
        
        self.retriever = Retriever(
            vector_store=self.vector_store,
            top_k=self.config['rag']['top_k']
        )
        
        self.ollama_url = f"{self.config['ollama']['base_url']}/api/generate"
        self.model = self.config['ollama']['model']
        
    def retrieve_context(self, query: str) -> List[Dict]:
        """Récupère les documents pertinents"""
        results = self.retriever.retrieve(
            query=query,
            threshold=self.config['rag']['similarity_threshold']
        )
        return results
    
    def format_context(self, results: List[Dict]) -> str:
        """Formate le contexte pour le prompt"""
        if not results:
            return "Aucun document pertinent trouvé."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Document {i}:")
            context_parts.append(result['text'])
            context_parts.append("")  # Ligne vide
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        """Génère une réponse avec Ollama"""
        # Créer le prompt complet
        system_prompt = self.config['prompts']['system']
        rag_template = self.config['prompts']['rag_template']
        
        full_prompt = f"{system_prompt}\n\n{rag_template}".format(
            context=context,
            question=query
        )
        
        # Appeler Ollama
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": self.config['ollama']['temperature']
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Erreur: {response.status_code}"
                
        except Exception as e:
            return f"Erreur lors de la génération: {str(e)}"
    
    def chat(self, query: str) -> Dict:
        """Fonction principale pour répondre à une question"""
        # 1. Récupérer les documents pertinents
        retrieved_docs = self.retrieve_context(query)
        
        # 2. Formater le contexte
        context = self.format_context(retrieved_docs)
        
        # 3. Générer la réponse
        response = self.generate_response(query, context)
        
        # 4. Retourner le résultat complet
        return {
            "query": query,
            "response": response,
            "sources": [
                {
                    "text": doc['text'][:200] + "...",
                    "score": doc['score']
                }
                for doc in retrieved_docs
            ],
            "num_sources": len(retrieved_docs)
        }

# Fonction pour tester l'agent
def test_agent():
    """Test simple de l'agent"""
    agent = RAGAgent()
    
    # Test avec une question
    result = agent.chat("Quelles sont les formations disponibles à l'ENSA ?")
    
    print("\n=== QUESTION ===")
    print(result['query'])
    
    print("\n=== RÉPONSE ===")
    print(result['response'])
    
    print(f"\n=== SOURCES ({result['num_sources']}) ===")
    for i, source in enumerate(result['sources'], 1):
        print(f"\n{i}. Score: {source['score']:.3f}")
        print(f"   {source['text']}")

if __name__ == "__main__":
    test_agent()