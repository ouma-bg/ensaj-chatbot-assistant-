import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class TextSplitter:
    """Découpe les documents en chunks"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or int(os.getenv('RAG_CHUNK_SIZE', 1000))
        self.chunk_overlap = chunk_overlap or int(os.getenv('RAG_CHUNK_OVERLAP', 200))
        print(f"✂️ Splitter: {self.chunk_size} chars, overlap {self.chunk_overlap}")
    
    def split_documents(self, documents: List) -> List:
        """Découper les documents en chunks"""
        chunks = []
        
        for doc in documents:
            text = doc.page_content
            doc_chunks = self._split_text(text)
            
            for i, chunk_text in enumerate(doc_chunks):
                # Créer un nouveau document pour chaque chunk
                chunk = type(doc)(
                    page_content=chunk_text,
                    metadata={
                        **doc.metadata,
                        "chunk_id": i,
                        "total_chunks": len(doc_chunks)
                    }
                )
                chunks.append(chunk)
        
        print(f"📦 {len(documents)} docs → {len(chunks)} chunks\n")
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """Découper un texte en morceaux avec overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
            # Éviter boucle infinie
            if start >= text_length:
                break
        
        return chunks