import os
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

class Retriever:
    """Récupère les documents pertinents"""
    
    def __init__(self, vector_store, top_k: int = None, score_threshold: float = None):
        self.vector_store = vector_store
        self.top_k = top_k or int(os.getenv('RAG_TOP_K', 5))
        self.score_threshold = score_threshold or float(os.getenv('RAG_SCORE_THRESHOLD', 0.7))
        print(f"🔍 Retriever: top_k={self.top_k}, threshold={self.score_threshold}")
    
    def retrieve(self, query: str) -> List[Tuple]:
        """Récupérer documents pertinents"""
        # Recherche par similarité
        results = self.vector_store.similarity_search(query, k=self.top_k)
        
        # Filtrer par score
        filtered_results = [
            (doc, score) for doc, score in results 
            if score >= self.score_threshold
        ]
        
        print(f"📋 {len(filtered_results)}/{len(results)} documents pertinents")
        return filtered_results
    
    def format_context(self, results: List[Tuple]) -> str:
        """Formater le contexte pour le LLM"""
        if not results:
            return "Aucun document pertinent trouvé."
        
        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', '')
            page_info = f" (page {page})" if page else ""
            
            context_parts.append(
                f"[Document {i} - {source}{page_info}]:\n{doc.page_content}\n"
            )
        
        return "\n".join(context_parts)