import os
from typing import List
from pathlib import Path
from pypdf import PdfReader

class Document:
    """Représente un document"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"Document(content={self.page_content[:50]}..., metadata={self.metadata})"

class DocumentLoader:
    """Charge des documents (PDF, TXT)"""
    
    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """Charger un PDF"""
        documents = []
        try:
            reader = PdfReader(file_path)
            filename = os.path.basename(file_path)
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": filename,
                            "page": i + 1,
                            "type": "pdf",
                            "path": file_path
                        }
                    )
                    documents.append(doc)
            
            print(f"📄 {filename}: {len(documents)} pages chargées")
        except Exception as e:
            print(f"❌ Erreur PDF {file_path}: {e}")
        
        return documents
    
    @staticmethod
    def load_txt(file_path: str) -> List[Document]:
        """Charger un fichier texte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            doc = Document(
                page_content=content,
                metadata={
                    "source": filename,
                    "type": "txt",
                    "path": file_path
                }
            )
            print(f"📝 {filename}: chargé")
            return [doc]
        except Exception as e:
            print(f"❌ Erreur TXT {file_path}: {e}")
            return []
    
    @staticmethod
    def load_directory(directory_path: str) -> List[Document]:
        """Charger tous les documents d'un dossier"""
        all_documents = []
        path = Path(directory_path)
        
        if not path.exists():
            print(f"⚠️ Dossier introuvable: {directory_path}")
            return []
        
        print(f"📂 Chargement depuis: {directory_path}")
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                if file_path.suffix.lower() == '.pdf':
                    docs = DocumentLoader.load_pdf(str(file_path))
                    all_documents.extend(docs)
                elif file_path.suffix.lower() == '.txt':
                    docs = DocumentLoader.load_txt(str(file_path))
                    all_documents.extend(docs)
        
        print(f"✅ Total: {len(all_documents)} documents chargés\n")
        return all_documents