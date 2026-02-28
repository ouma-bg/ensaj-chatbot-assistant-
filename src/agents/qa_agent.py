from typing import List, Tuple, Dict
from .base_agent import BaseAgent
from ..prompts.prompt_templates import PromptTemplates

class QAAgent(BaseAgent):
    """Agent spécialisé Q&A avec RAG"""
    
    def __init__(self, retriever=None, model_name: str = None):
        super().__init__(model_name)
        self.retriever = retriever
        self.conversation_history = []
        print("💬 QA Agent prêt")
    
    def answer(self, question: str, use_rag: bool = True) -> Dict:
        """Répondre à une question"""
        
        # Récupérer contexte si RAG activé
        context = ""
        sources = []
        
        if use_rag and self.retriever:
            results = self.retriever.retrieve(question)
            
            if results:
                context = self.retriever.format_context(results)
                sources = [
                    {
                        "source": doc.metadata.get("source", "Unknown"),
                        "page": doc.metadata.get("page", ""),
                        "score": round(score, 3)
                    }
                    for doc, score in results
                ]
            else:
                # Pas de résultats pertinents
                return {
                    "answer": PromptTemplates.get_fallback_response(),
                    "sources": [],
                    "has_context": False
                }
        
        # Générer prompt
        if context:
            prompt = PromptTemplates.get_rag_prompt(context, question)
        else:
            prompt = f"{PromptTemplates.SYSTEM_PROMPT}\n\nQuestion: {question}"
        
        # Générer réponse
        answer = self.generate(prompt)
        
        # Sauvegarder dans l'historique
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "sources": sources
        })
        
        return {
            "answer": answer,
            "sources": sources,
            "has_context": bool(context)
        }
    
    def chat_with_history(self, message: str) -> str:
        """Chat avec historique de conversation"""
        messages = [
            {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT}
        ]
        
        # Ajouter historique
        for entry in self.conversation_history[-5:]:  # 5 derniers messages
            messages.append({"role": "user", "content": entry["question"]})
            messages.append({"role": "assistant", "content": entry["answer"]})
        
        # Nouveau message
        messages.append({"role": "user", "content": message})
        
        return self.chat(messages)
    
    def clear_history(self):
        """Effacer l'historique"""
        self.conversation_history = []
        print("🗑️ Historique effacé")