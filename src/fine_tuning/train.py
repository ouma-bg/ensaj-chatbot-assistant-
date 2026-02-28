"""
Script pour fine-tuner un modèle Ollama avec des données spécifiques à l'ENSA
"""

import json
import yaml
import subprocess
from pathlib import Path
from typing import List, Dict

class OllamaFineTuner:
    """Classe pour fine-tuner des modèles avec Ollama"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialise le fine-tuner"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.training_file = self.config['fine_tuning']['training_file']
        self.base_model = self.config['fine_tuning']['model_name']
        self.output_model = self.config['fine_tuning']['output_model']
        
    def load_training_data(self) -> List[Dict]:
        """Charge les données d'entraînement depuis le fichier JSONL"""
        data = []
        with open(self.training_file, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        
        print(f"✅ Chargé {len(data)} exemples d'entraînement")
        return data
    
    def create_modelfile(self, training_data: List[Dict]) -> str:
        """Crée un Modelfile pour Ollama avec les exemples"""
        
        # Créer le système prompt enrichi
        system_prompt = self.config['prompts']['system']
        
        # Ajouter des exemples au prompt
        examples = "\n\n=== EXEMPLES ===\n"
        for i, example in enumerate(training_data[:5], 1):  # Premiers 5 exemples
            examples += f"\nExemple {i}:\n"
            examples += f"Question: {example['prompt']}\n"
            examples += f"Réponse: {example['completion']}\n"
        
        full_system = system_prompt + examples
        
        # Créer le Modelfile
        modelfile_content = f'''FROM {self.base_model}

# Paramètres du modèle
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

# Prompt système avec exemples
SYSTEM """
{full_system}
"""
'''
        
        # Sauvegarder le Modelfile
        modelfile_path = Path("./src/fine_tuning/Modelfile")
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        print(f"✅ Modelfile créé: {modelfile_path}")
        return str(modelfile_path)
    
    def create_model(self, modelfile_path: str) -> bool:
        """Crée le modèle personnalisé avec Ollama"""
        try:
            print(f"\n🚀 Création du modèle '{self.output_model}'...")
            print("Cela peut prendre quelques minutes...\n")
            
            # Commande pour créer le modèle
            cmd = f"ollama create {self.output_model} -f {modelfile_path}"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Modèle '{self.output_model}' créé avec succès!")
                return True
            else:
                print(f"❌ Erreur: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
            return False
    
    def test_model(self):
        """Teste le modèle fine-tuné"""
        print(f"\n🧪 Test du modèle '{self.output_model}'...\n")
        
        test_questions = [
            "Quelles sont les filières à l'ENSA ?",
            "Comment s'inscrire ?",
            "Combien de temps durent les études ?"
        ]
        
        for question in test_questions:
            print(f"❓ Question: {question}")
            
            cmd = f'ollama run {self.output_model} "{question}"'
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"💬 Réponse: {result.stdout}\n")
                else:
                    print(f"❌ Erreur: {result.stderr}\n")
                    
            except subprocess.TimeoutExpired:
                print("⏱️ Timeout - La génération a pris trop de temps\n")
    
    def train(self):
        """Processus complet de fine-tuning"""
        print("=" * 60)
        print("🎓 FINE-TUNING DU CHATBOT ENSA")
        print("=" * 60)
        
        # 1. Charger les données
        print("\n📊 Étape 1: Chargement des données")
        training_data = self.load_training_data()
        
        # 2. Créer le Modelfile
        print("\n📝 Étape 2: Création du Modelfile")
        modelfile_path = self.create_modelfile(training_data)
        
        # 3. Créer le modèle
        print("\n⚙️ Étape 3: Création du modèle personnalisé")
        success = self.create_model(modelfile_path)
        
        if success:
            # 4. Tester le modèle
            print("\n✨ Étape 4: Test du modèle")
            self.test_model()
            
            print("\n" + "=" * 60)
            print("✅ FINE-TUNING TERMINÉ!")
            print(f"Vous pouvez maintenant utiliser le modèle: {self.output_model}")
            print("=" * 60)
        else:
            print("\n❌ Le fine-tuning a échoué")

def main():
    """Fonction principale"""
    # Créer et lancer le fine-tuner
    tuner = OllamaFineTuner()
    tuner.train()

if __name__ == "__main__":
    main()