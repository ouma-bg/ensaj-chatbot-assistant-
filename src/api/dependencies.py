"""
Dépendances FastAPI (authentification, etc.)
"""

import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

async def verify_api_key(x_api_key: str = Header(None)):
    """
    Vérifier la clé API (optionnel pour développement)
    """
    # En mode DEBUG, on skip la vérification
    if os.getenv('DEBUG', 'False').lower() == 'true':
        return True
    
    expected_key = os.getenv('API_KEY')
    if not expected_key:
        return True  # Pas de clé configurée
    
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=403,
            detail="Clé API invalide"
        )
    
    return True