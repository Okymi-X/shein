#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Script de Configuration et Installation
Script d'aide pour configurer rapidement le système SHEIN_SEN
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import shutil

class SheinSenSetup:
    """Assistant de configuration SHEIN_SEN"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_installed = False
        
    def print_banner(self):
        """Afficher la bannière de bienvenue"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                        🛍️ SHEIN_SEN 🛍️                        ║
║        Système d'Automatisation des Commandes Groupées       ║
║                    Shein au Sénégal 🇸🇳                       ║
╚══════════════════════════════════════════════════════════════╝

🚀 Assistant de Configuration et Installation
        """)
    
    def check_python_version(self) -> bool:
        """Vérifier la version de Python"""
        print("🐍 Vérification de la version Python...")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ requis. Version actuelle:", sys.version)
            return False
        
        print(f"✅ Python {sys.version.split()[0]} détecté")
        return True
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Vérifier les dépendances système"""
        print("\n📦 Vérification des dépendances...")
        
        dependencies = {
            'pip': False,
            'git': False,
            'chrome': False
        }
        
        # Vérifier pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         capture_output=True, check=True)
            dependencies['pip'] = True
            print("✅ pip disponible")
        except subprocess.CalledProcessError:
            print("❌ pip non trouvé")
        
        # Vérifier git
        try:
            subprocess.run(['git', '--version'], 
                         capture_output=True, check=True)
            dependencies['git'] = True
            print("✅ git disponible")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ git non trouvé (optionnel)")
        
        # Vérifier Chrome/Chromium
        chrome_paths = [
            'google-chrome',
            'chromium-browser',
            'chromium',
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        ]
        
        for chrome_path in chrome_paths:
            if shutil.which(chrome_path) or Path(chrome_path).exists():
                dependencies['chrome'] = True
                print("✅ Chrome/Chromium trouvé")
                break
        
        if not dependencies['chrome']:
            print("⚠️ Chrome/Chromium non trouvé (requis pour Playwright)")
        
        return dependencies
    
    def install_requirements(self) -> bool:
        """Installer les dépendances Python"""
        print("\n📥 Installation des dépendances Python...")
        
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            print("❌ Fichier requirements.txt non trouvé")
            return False
        
        try:
            # Installer les requirements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], check=True)
            
            print("✅ Dépendances Python installées")
            
            # Installer Playwright browsers
            print("🎭 Installation des navigateurs Playwright...")
            subprocess.run([
                sys.executable, '-m', 'playwright', 'install', 'chromium'
            ], check=True)
            
            print("✅ Navigateurs Playwright installés")
            self.requirements_installed = True
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation: {e}")
            return False
    
    def create_directories(self):
        """Créer les répertoires nécessaires"""
        print("\n📁 Création des répertoires...")
        
        directories = [
            'data',
            'data/backups',
            'logs',
            'cookies'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            print(f"✅ {directory}/")
    
    def setup_environment_file(self):
        """Configurer le fichier d'environnement"""
        print("\n⚙️ Configuration du fichier d'environnement...")
        
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if env_file.exists():
            response = input("📄 Le fichier .env existe déjà. Le remplacer? (y/N): ")
            if response.lower() != 'y':
                print("⏭️ Configuration .env ignorée")
                return
        
        if env_example.exists():
            shutil.copy2(env_example, env_file)
            print("✅ Fichier .env créé à partir de .env.example")
            print("⚠️ IMPORTANT: Éditez le fichier .env avec vos vraies clés API")
        else:
            print("❌ Fichier .env.example non trouvé")
    
    def interactive_config(self):
        """Configuration interactive des clés API"""
        print("\n🔑 Configuration interactive des clés API")
        print("(Appuyez sur Entrée pour ignorer)")
        
        config = {}
        
        # OpenAI API Key
        openai_key = input("🤖 Clé API OpenAI (sk-...): ").strip()
        if openai_key:
            config['OPENAI_API_KEY'] = openai_key
        
        # Twilio Configuration
        print("\n📱 Configuration Twilio WhatsApp:")
        twilio_sid = input("   Account SID: ").strip()
        if twilio_sid:
            config['TWILIO_ACCOUNT_SID'] = twilio_sid
        
        twilio_token = input("   Auth Token: ").strip()
        if twilio_token:
            config['TWILIO_AUTH_TOKEN'] = twilio_token
        
        twilio_number = input("   Numéro WhatsApp (whatsapp:+14155238886): ").strip()
        if twilio_number:
            config['TWILIO_WHATSAPP_NUMBER'] = twilio_number
        
        # Admin WhatsApp
        admin_number = input("👤 Numéro Admin WhatsApp (whatsapp:+221XXXXXXXXX): ").strip()
        if admin_number:
            config['ADMIN_WHATSAPP_NUMBER'] = admin_number
        
        # Sauvegarder la configuration
        if config:
            self.update_env_file(config)
            print("✅ Configuration sauvegardée dans .env")
        else:
            print("⏭️ Aucune configuration fournie")
    
    def update_env_file(self, config: Dict[str, str]):
        """Mettre à jour le fichier .env"""
        env_file = self.project_root / '.env'
        
        # Lire le fichier existant
        lines = []
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Mettre à jour les valeurs
        updated_lines = []
        updated_keys = set()
        
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0]
                if key in config:
                    updated_lines.append(f"{key}={config[key]}\n")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')
        
        # Ajouter les nouvelles clés
        for key, value in config.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}\n")
        
        # Sauvegarder
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
    
    def test_configuration(self) -> bool:
        """Tester la configuration"""
        print("\n🧪 Test de la configuration...")
        
        try:
            # Importer et tester la configuration
            sys.path.insert(0, str(self.project_root))
            from config import Config
            
            # Tester la création des répertoires
            Config.create_directories()
            print("✅ Création des répertoires")
            
            # Tester la validation de la config
            if Config.validate_config():
                print("✅ Configuration valide")
                return True
            else:
                print("⚠️ Configuration incomplète (clés API manquantes)")
                return False
                
        except Exception as e:
            print(f"❌ Erreur test configuration: {e}")
            return False
    
    def create_sample_data(self):
        """Créer des données d'exemple"""
        print("\n📊 Création de données d'exemple...")
        
        try:
            sys.path.insert(0, str(self.project_root))
            from data_manager import DataManager
            
            dm = DataManager()
            
            # Ajouter quelques commandes d'exemple
            sample_orders = [
                {
                    'user_phone': 'whatsapp:+221701234567',
                    'user_name': 'Awa Diop',
                    'product_url': 'https://www.shein.com/fr/item12345',
                    'size': 'M',
                    'color': 'Rouge',
                    'quantity': 2,
                    'estimated_price': 15.99
                },
                {
                    'user_phone': 'whatsapp:+221707654321',
                    'user_name': 'Fatou Sall',
                    'product_url': 'https://www.shein.com/fr/item67890',
                    'size': 'L',
                    'color': 'Bleu',
                    'quantity': 1,
                    'estimated_price': 22.50
                }
            ]
            
            for order in sample_orders:
                dm.add_order(**order)
            
            print("✅ Données d'exemple créées")
            
        except Exception as e:
            print(f"❌ Erreur création données d'exemple: {e}")
    
    def show_next_steps(self):
        """Afficher les prochaines étapes"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 Installation Terminée! 🎉               ║
╚══════════════════════════════════════════════════════════════╝

📋 Prochaines étapes:

1. 🔑 Configurez vos clés API dans le fichier .env
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Twilio: https://www.twilio.com/console

2. 📱 Configurez WhatsApp Sandbox Twilio:
   - Allez sur: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Configurez le webhook: https://your-domain.com/webhook

3. 🚀 Démarrez le système:
   python main.py

4. 🧪 Testez avec WhatsApp:
   Envoyez un lien Shein à votre numéro Twilio

5. 📊 Vérifiez le statut:
   http://localhost:5000/status

📚 Documentation complète: README.md

🆘 Support: Consultez les logs dans le dossier logs/
        """)
    
    def run_setup(self):
        """Exécuter la configuration complète"""
        self.print_banner()
        
        # Vérifications préliminaires
        if not self.check_python_version():
            return False
        
        dependencies = self.check_dependencies()
        if not dependencies['pip']:
            print("❌ pip est requis pour continuer")
            return False
        
        # Installation
        if not self.install_requirements():
            print("❌ Échec installation des dépendances")
            return False
        
        # Configuration
        self.create_directories()
        self.setup_environment_file()
        
        # Configuration interactive
        response = input("\n🔧 Voulez-vous configurer les clés API maintenant? (y/N): ")
        if response.lower() == 'y':
            self.interactive_config()
        
        # Tests
        self.test_configuration()
        
        # Données d'exemple
        response = input("\n📊 Créer des données d'exemple? (y/N): ")
        if response.lower() == 'y':
            self.create_sample_data()
        
        # Finalisation
        self.show_next_steps()
        return True

def main():
    """Point d'entrée principal"""
    try:
        setup = SheinSenSetup()
        success = setup.run_setup()
        
        if success:
            print("\n✅ Configuration terminée avec succès!")
            return 0
        else:
            print("\n❌ Échec de la configuration")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Configuration interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())