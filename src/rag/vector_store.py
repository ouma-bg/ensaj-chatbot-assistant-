import os
import pickle
from typing import List, Tuple
import faiss
import numpy as np
from pathlib import Path

class VectorStore:  # ← BADELT MEN FAISSVectorStore L VectorStore
    """Store vectoriel avec FAISS"""
    
    def __init__(self, embedding_function, dimension: int = 768):
        self.embedding_function = embedding_function
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.doc_embeddings = []
        print(f"🗄️ FAISS Vector Store initialisé (dim={dimension})")
    
    def add_documents(self, documents: List, embeddings: List[List[float]] = None):
        """Ajouter des documents au store"""
        if embeddings is None:
            texts = [doc.page_content for doc in documents]
            embeddings = self.embedding_function.embed_documents(texts)
        
        # Convertir en numpy array
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Ajouter à l'index FAISS
        self.index.add(embeddings_np)
        
        # Sauvegarder documents et embeddings
        self.documents.extend(documents)
        self.doc_embeddings.extend(embeddings)
        
        print(f"✅ {len(documents)} documents ajoutés au vector store")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple]:
        """Rechercher les documents les plus similaires"""
        # Générer embedding de la requête
        query_embedding = self.embedding_function.embed_query(query)
        query_np = np.array([query_embedding]).astype('float32')
        
        # Rechercher dans FAISS
        distances, indices = self.index.search(query_np, k)
        
        # Retourner documents avec scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                # Convertir distance L2 en score de similarité
                score = 1 / (1 + distances[0][i])
                results.append((self.documents[idx], score))
        
        return results
    
    def save(self, path: str):
        """Sauvegarder l'index"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder l'index FAISS
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        
        # Sauvegarder documents et métadonnées
        with open(os.path.join(path, "documents.pkl"), 'wb') as f:
            pickle.dump(self.documents, f)
        
        with open(os.path.join(path, "embeddings.pkl"), 'wb') as f:
            pickle.dump(self.doc_embeddings, f)
        
        print(f"💾 Vector store sauvegardé: {path}")
    
    def load(self, path: str):
        """Charger l'index"""
        # Charger l'index FAISS
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        
        # Charger documents
        with open(os.path.join(path, "documents.pkl"), 'rb') as f:
            self.documents = pickle.load(f)
        
        # Charger embeddings
        with open(os.path.join(path, "embeddings.pkl"), 'rb') as f:
            self.doc_embeddings = pickle.load(f)
        
        print(f"📂 Vector store chargé: {len(self.documents)} documents")


# Alias pour compatibilité
FAISSVectorStore = VectorStore