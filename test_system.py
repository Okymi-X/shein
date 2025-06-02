#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Script de Test du Système
Script pour tester tous les composants du système SHEIN_SEN
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import traceback
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

class SheinSenTester:
    """Testeur pour le système SHEIN_SEN"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.errors = []
        
    def print_header(self, title: str):
        """Afficher un en-tête de section"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, success: bool, details: str = ""):
        """Afficher le résultat d'un test"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_imports(self) -> bool:
        """Tester les imports des modules"""
        self.print_header("Test des Imports")
        
        modules_to_test = [
            ('config', 'Config'),
            ('data_manager', 'DataManager'),
            ('ai_processor', 'AIProcessor'),
            ('shein_bot', 'SheinBot'),
            ('recap_export', 'RecapExporter'),
            ('whatsapp_listener', 'WhatsAppListener'),
            ('main', 'SheinSenOrchestrator')
        ]
        
        all_success = True
        
        for module_name, class_name in modules_to_test:
            try:
                module = __import__(module_name)
                if hasattr(module, class_name):
                    self.print_test(f"Import {module_name}.{class_name}", True)
                else:
                    self.print_test(f"Import {module_name}.{class_name}", False, 
                                  f"Classe {class_name} non trouvée")
                    all_success = False
            except Exception as e:
                self.print_test(f"Import {module_name}", False, str(e))
                all_success = False
                self.errors.append(f"Import {module_name}: {e}")
        
        return all_success
    
    def test_configuration(self) -> bool:
        """Tester la configuration"""
        self.print_header("Test de Configuration")
        
        try:
            from config import Config
            
            # Test création des répertoires
            try:
                Config.create_directories()
                self.print_test("Création des répertoires", True)
            except Exception as e:
                self.print_test("Création des répertoires", False, str(e))
                return False
            
            # Test validation de la config
            try:
                is_valid = Config.validate_config()
                if is_valid:
                    self.print_test("Validation configuration", True, "Toutes les clés API sont présentes")
                else:
                    self.print_test("Validation configuration", False, "Clés API manquantes (normal si pas encore configuré)")
            except Exception as e:
                self.print_test("Validation configuration", False, str(e))
                return False
            
            # Test des constantes
            required_attrs = ['OPENAI_API_KEY', 'DATA_DIR', 'COOKIES_DIR', 'LOGS_DIR']
            for attr in required_attrs:
                if hasattr(Config, attr):
                    self.print_test(f"Constante {attr}", True)
                else:
                    self.print_test(f"Constante {attr}", False, "Attribut manquant")
                    return False
            
            return True
            
        except Exception as e:
            self.print_test("Configuration générale", False, str(e))
            self.errors.append(f"Configuration: {e}")
            return False
    
    def test_data_manager(self) -> bool:
        """Tester le gestionnaire de données"""
        self.print_header("Test du Gestionnaire de Données")
        
        try:
            from data_manager import DataManager
            
            # Initialisation
            try:
                dm = DataManager()
                self.print_test("Initialisation DataManager", True)
            except Exception as e:
                self.print_test("Initialisation DataManager", False, str(e))
                return False
            
            # Test ajout d'une commande
            try:
                order_id = dm.add_order(
                    user_phone="whatsapp:+221701234567",
                    user_name="Test User",
                    product_url="https://www.shein.com/fr/test123",
                    size="M",
                    color="Rouge",
                    quantity=1,
                    estimated_price=15.99
                )
                self.print_test("Ajout commande", True, f"ID: {order_id}")
            except Exception as e:
                self.print_test("Ajout commande", False, str(e))
                return False
            
            # Test récupération des commandes
            try:
                orders = dm.get_user_orders("whatsapp:+221701234567")
                if orders:
                    self.print_test("Récupération commandes utilisateur", True, f"{len(orders)} commande(s)")
                else:
                    self.print_test("Récupération commandes utilisateur", False, "Aucune commande trouvée")
            except Exception as e:
                self.print_test("Récupération commandes utilisateur", False, str(e))
                return False
            
            # Test statistiques
            try:
                stats = dm.get_statistics()
                self.print_test("Statistiques", True, f"Total: {stats.get('total_orders', 0)} commandes")
            except Exception as e:
                self.print_test("Statistiques", False, str(e))
                return False
            
            return True
            
        except Exception as e:
            self.print_test("DataManager général", False, str(e))
            self.errors.append(f"DataManager: {e}")
            return False
    
    def test_ai_processor(self) -> bool:
        """Tester le processeur IA"""
        self.print_header("Test du Processeur IA")
        
        try:
            from ai_processor import AIProcessor
            
            # Initialisation
            try:
                ai = AIProcessor()
                self.print_test("Initialisation AIProcessor", True)
            except Exception as e:
                self.print_test("Initialisation AIProcessor", False, str(e))
                return False
            
            # Test nettoyage de message
            try:
                test_message = "Salut! Voici le lien: https://www.shein.com/fr/test123 - Taille M, couleur rouge, quantité 2"
                cleaned = ai.clean_message(test_message)
                self.print_test("Nettoyage message", True, f"Longueur: {len(cleaned)} caractères")
            except Exception as e:
                self.print_test("Nettoyage message", False, str(e))
                return False
            
            # Test extraction basique
            try:
                basic_info = ai.extract_basic_info(test_message)
                if basic_info.get('product_url'):
                    self.print_test("Extraction basique", True, f"URL trouvée: {basic_info['product_url']}")
                else:
                    self.print_test("Extraction basique", False, "Aucune URL trouvée")
            except Exception as e:
                self.print_test("Extraction basique", False, str(e))
                return False
            
            # Test extraction avancée (seulement si clé API disponible)
            try:
                from config import Config
                if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY.startswith('sk-'):
                    advanced_info = ai.extract_with_ai(test_message, "Test User")
                    if advanced_info:
                        self.print_test("Extraction IA", True, "Extraction réussie")
                    else:
                        self.print_test("Extraction IA", False, "Aucune information extraite")
                else:
                    self.print_test("Extraction IA", False, "Clé API OpenAI non configurée (normal)")
            except Exception as e:
                self.print_test("Extraction IA", False, str(e))
            
            return True
            
        except Exception as e:
            self.print_test("AIProcessor général", False, str(e))
            self.errors.append(f"AIProcessor: {e}")
            return False
    
    def test_shein_bot(self) -> bool:
        """Tester le bot Shein"""
        self.print_header("Test du Bot Shein")
        
        try:
            from shein_bot import SheinBot
            
            # Initialisation
            try:
                bot = SheinBot()
                self.print_test("Initialisation SheinBot", True)
            except Exception as e:
                self.print_test("Initialisation SheinBot", False, str(e))
                return False
            
            # Test vérification des cookies
            try:
                has_cookies = bot.has_valid_cookies()
                self.print_test("Vérification cookies", True, 
                              f"Cookies {'valides' if has_cookies else 'non trouvés'}")
            except Exception as e:
                self.print_test("Vérification cookies", False, str(e))
                return False
            
            # Test validation URL
            try:
                valid_url = bot.is_valid_shein_url("https://www.shein.com/fr/test123")
                invalid_url = bot.is_valid_shein_url("https://example.com")
                
                if valid_url and not invalid_url:
                    self.print_test("Validation URL", True, "URLs correctement validées")
                else:
                    self.print_test("Validation URL", False, "Problème de validation")
            except Exception as e:
                self.print_test("Validation URL", False, str(e))
                return False
            
            return True
            
        except Exception as e:
            self.print_test("SheinBot général", False, str(e))
            self.errors.append(f"SheinBot: {e}")
            return False
    
    def test_recap_export(self) -> bool:
        """Tester l'exportateur de récapitulatifs"""
        self.print_header("Test de l'Exportateur")
        
        try:
            from recap_export import RecapExporter
            from data_manager import DataManager
            
            # Initialisation
            try:
                dm = DataManager()
                exporter = RecapExporter(dm)
                self.print_test("Initialisation RecapExporter", True)
            except Exception as e:
                self.print_test("Initialisation RecapExporter", False, str(e))
                return False
            
            # Test génération Excel
            try:
                excel_path = exporter.generate_excel_report()
                if excel_path and Path(excel_path).exists():
                    self.print_test("Génération Excel", True, f"Fichier: {excel_path}")
                else:
                    self.print_test("Génération Excel", False, "Fichier non créé")
            except Exception as e:
                self.print_test("Génération Excel", False, str(e))
                return False
            
            # Test génération PDF
            try:
                pdf_path = exporter.generate_pdf_summary()
                if pdf_path and Path(pdf_path).exists():
                    self.print_test("Génération PDF", True, f"Fichier: {pdf_path}")
                else:
                    self.print_test("Génération PDF", False, "Fichier non créé")
            except Exception as e:
                self.print_test("Génération PDF", False, str(e))
                return False
            
            # Test récapitulatif WhatsApp
            try:
                whatsapp_summary = exporter.get_whatsapp_summary()
                if whatsapp_summary:
                    self.print_test("Récapitulatif WhatsApp", True, f"Longueur: {len(whatsapp_summary)} caractères")
                else:
                    self.print_test("Récapitulatif WhatsApp", False, "Récapitulatif vide")
            except Exception as e:
                self.print_test("Récapitulatif WhatsApp", False, str(e))
                return False
            
            return True
            
        except Exception as e:
            self.print_test("RecapExporter général", False, str(e))
            self.errors.append(f"RecapExporter: {e}")
            return False
    
    def test_whatsapp_listener(self) -> bool:
        """Tester l'écouteur WhatsApp"""
        self.print_header("Test de l'Écouteur WhatsApp")
        
        try:
            from whatsapp_listener import WhatsAppListener
            
            # Initialisation
            try:
                listener = WhatsAppListener()
                self.print_test("Initialisation WhatsAppListener", True)
            except Exception as e:
                self.print_test("Initialisation WhatsAppListener", False, str(e))
                return False
            
            # Test validation numéro
            try:
                valid_number = listener.is_valid_whatsapp_number("whatsapp:+221701234567")
                invalid_number = listener.is_valid_whatsapp_number("invalid")
                
                if valid_number and not invalid_number:
                    self.print_test("Validation numéro WhatsApp", True, "Numéros correctement validés")
                else:
                    self.print_test("Validation numéro WhatsApp", False, "Problème de validation")
            except Exception as e:
                self.print_test("Validation numéro WhatsApp", False, str(e))
                return False
            
            # Test formatage message
            try:
                formatted = listener.format_confirmation_message("Test User", "https://www.shein.com/fr/test123")
                if formatted and "Test User" in formatted:
                    self.print_test("Formatage message", True, "Message correctement formaté")
                else:
                    self.print_test("Formatage message", False, "Problème de formatage")
            except Exception as e:
                self.print_test("Formatage message", False, str(e))
                return False
            
            return True
            
        except Exception as e:
            self.print_test("WhatsAppListener général", False, str(e))
            self.errors.append(f"WhatsAppListener: {e}")
            return False
    
    def test_main_orchestrator(self) -> bool:
        """Tester l'orchestrateur principal"""
        self.print_header("Test de l'Orchestrateur Principal")
        
        try:
            from main import SheinSenOrchestrator
            
            # Initialisation
            try:
                orchestrator = SheinSenOrchestrator()
                self.print_test("Initialisation Orchestrateur", True)
            except Exception as e:
                self.print_test("Initialisation Orchestrateur", False, str(e))
                return False
            
            # Test statut système
            try:
                status = orchestrator.get_system_status()
                if status and 'status' in status:
                    self.print_test("Statut système", True, f"Statut: {status['status']}")
                else:
                    self.print_test("Statut système", False, "Statut non disponible")
            except Exception as e:
                self.print_test("Statut système", False, str(e))
                return False
            
            # Test métriques performance
            try:
                metrics = orchestrator.get_performance_metrics()
                if metrics:
                    self.print_test("Métriques performance", True, f"{len(metrics)} métriques")
                else:
                    self.print_test("Métriques performance", False, "Métriques non disponibles")
            except Exception as e:
                self.print_test("Métriques performance", False, str(e))
                return False
            
            return True
            
        except Exception as e:
            self.print_test("Orchestrateur général", False, str(e))
            self.errors.append(f"Orchestrateur: {e}")
            return False
    
    def test_file_structure(self) -> bool:
        """Tester la structure des fichiers"""
        self.print_header("Test de la Structure des Fichiers")
        
        required_files = [
            'config.py',
            'data_manager.py',
            'ai_processor.py',
            'shein_bot.py',
            'recap_export.py',
            'whatsapp_listener.py',
            'main.py',
            'requirements.txt',
            'README.md',
            '.env.example'
        ]
        
        required_dirs = [
            'data',
            'logs',
            'cookies'
        ]
        
        all_success = True
        
        # Vérifier les fichiers
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.print_test(f"Fichier {file_name}", True)
            else:
                self.print_test(f"Fichier {file_name}", False, "Fichier manquant")
                all_success = False
        
        # Vérifier les répertoires
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.print_test(f"Répertoire {dir_name}/", True)
            else:
                self.print_test(f"Répertoire {dir_name}/", False, "Répertoire manquant")
                all_success = False
        
        return all_success
    
    def generate_test_report(self):
        """Générer un rapport de test"""
        self.print_header("Rapport de Test")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"\n📊 Résumé des Tests:")
        print(f"   Total: {total_tests}")
        print(f"   ✅ Réussis: {successful_tests}")
        print(f"   ❌ Échoués: {failed_tests}")
        print(f"   📈 Taux de réussite: {(successful_tests/total_tests*100):.1f}%")
        
        if self.errors:
            print(f"\n🚨 Erreurs détectées:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        # Sauvegarder le rapport
        report_path = self.project_root / 'logs' / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': successful_tests/total_tests*100 if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'errors': self.errors
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport sauvegardé: {report_path}")
        
        return successful_tests == total_tests
    
    def run_all_tests(self) -> bool:
        """Exécuter tous les tests"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    🧪 SHEIN_SEN Test Suite 🧪                ║
║              Test de tous les composants système             ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        tests = [
            ('Structure des fichiers', self.test_file_structure),
            ('Imports des modules', self.test_imports),
            ('Configuration', self.test_configuration),
            ('Gestionnaire de données', self.test_data_manager),
            ('Processeur IA', self.test_ai_processor),
            ('Bot Shein', self.test_shein_bot),
            ('Exportateur', self.test_recap_export),
            ('Écouteur WhatsApp', self.test_whatsapp_listener),
            ('Orchestrateur principal', self.test_main_orchestrator)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔄 Exécution: {test_name}...")
                test_func()
            except Exception as e:
                self.print_test(f"Test {test_name}", False, f"Erreur inattendue: {e}")
                self.errors.append(f"Test {test_name}: {e}")
                traceback.print_exc()
        
        return self.generate_test_report()

def main():
    """Point d'entrée principal"""
    try:
        tester = SheinSenTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 Tous les tests sont passés avec succès!")
            print("✅ Le système SHEIN_SEN est prêt à être utilisé.")
            return 0
        else:
            print("\n⚠️ Certains tests ont échoué.")
            print("📋 Consultez le rapport de test pour plus de détails.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())