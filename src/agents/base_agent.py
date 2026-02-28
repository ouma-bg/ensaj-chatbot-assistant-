import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    """Agent de base pour interaction avec Ollama"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.max_tokens = int(os.getenv('MAX_TOKENS', 2048))
        self.temperature = float(os.getenv('TEMPERATURE', 0.7))
        print(f"🤖 Agent initialisé: {self.model_name}")
    
    def generate(self, prompt: str, stream: bool = False) -> str:
        """Générer une réponse"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": stream,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json().get("response", "")
        
        except Exception as e:
            print(f"❌ Erreur génération: {e}")
            return "Désolé, une erreur s'est produite. Veuillez réessayer."
    
    def _handle_stream(self, response):
        """Gérer les réponses en streaming"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                import json
                try:
                    chunk = json.loads(data)
                    if 'response' in chunk:
                        full_response += chunk['response']
                except:
                    continue
        return full_response
    
    def chat(self, messages: list) -> str:
        """Mode chat avec historique"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        
        except Exception as e:
            print(f"❌ Erreur chat: {e}")
            return "Désolé, une erreur s'est produite."