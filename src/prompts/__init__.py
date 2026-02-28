"""
Module de gestion des prompts
"""

from .prompt_templates import (
    SYSTEM_PROMPT,
    RAG_TEMPLATE,
    CHAT_TEMPLATE,
    get_prompt
)

__all__ = [
    'SYSTEM_PROMPT',
    'RAG_TEMPLATE', 
    'CHAT_TEMPLATE',
    'get_prompt'
]