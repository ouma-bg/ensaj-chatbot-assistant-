"""
Script pour nettoyer tous les fichiers cache Python
Exécuter: python clean_cache.py
"""

import os
import shutil
from pathlib import Path

def clean_pycache(root_dir="."):
    """Supprime tous les dossiers __pycache__ et fichiers .pyc"""
    
    root_path = Path(root_dir)
    deleted_count = 0
    
    print("🧹 Nettoyage des caches Python...\n")
    
    # Supprimer __pycache__ directories
    for pycache_dir in root_path.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            print(f"✅ Supprimé: {pycache_dir}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Erreur: {pycache_dir} - {e}")
    
    # Supprimer .pyc files
    for pyc_file in root_path.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            print(f"✅ Supprimé: {pyc_file}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Erreur: {pyc_file} - {e}")
    
    # Supprimer .pyo files
    for pyo_file in root_path.rglob("*.pyo"):
        try:
            pyo_file.unlink()
            print(f"✅ Supprimé: {pyo_file}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Erreur: {pyo_file} - {e}")
    
    print(f"\n🎉 Nettoyage terminé! {deleted_count} élément(s) supprimé(s)")
    print("\n💡 Maintenant, relancez votre script:")
    print("   python src/agents/rag_agent.py")

if __name__ == "__main__":
    clean_pycache()