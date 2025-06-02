# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Orchestrateur Principal
Système d'Automatisation des Commandes Groupées Shein au Sénégal
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
import schedule
from loguru import logger

from config import Config
from whatsapp_listener import WhatsAppListener
from ai_processor import AIProcessor
from data_manager import DataManager
from shein_bot import SheinBot
from recap_export import RecapExporter

class SheinSenOrchestrator:
    """Orchestrateur principal du système SHEIN_SEN"""
    
    def __init__(self):
        self.setup_logging()
        self.initialize_components()
        self.running = False
        self.stats = {
            'start_time': None,
            'messages_processed': 0,
            'orders_added': 0,
            'errors': 0,
            'last_activity': None
        }
    
    def setup_logging(self):
        """Configuration des logs centralisés"""
        logger.add(
            f"{Config.LOGS_DIR}/shein_sen_main.log",
            rotation="1 day",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        
        logger.add(
            f"{Config.LOGS_DIR}/shein_sen_errors.log",
            rotation="1 day",
            retention="30 days",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
    
    def initialize_components(self):
        """Initialiser tous les composants du système"""
        try:
            logger.info("🚀 Initialisation de SHEIN_SEN...")
            
            # Créer les répertoires nécessaires
            Config.create_directories()
            
            # Valider la configuration
            if not Config.validate_config():
                raise Exception("Configuration invalide - Vérifiez vos clés API")
            
            # Initialiser les composants
            self.data_manager = DataManager()
            self.ai_processor = AIProcessor()
            self.shein_bot = SheinBot()
            self.recap_exporter = RecapExporter()
            self.whatsapp_listener = WhatsAppListener()
            
            # Configurer les callbacks
            self.setup_callbacks()
            
            logger.info("✅ Tous les composants initialisés avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            raise
    
    def setup_callbacks(self):
        """Configurer les callbacks entre composants"""
        # Callback pour traitement automatique des commandes
        self.whatsapp_listener.set_order_callback(self.process_new_order)
        
        # Callback pour statistiques
        self.whatsapp_listener.set_stats_callback(self.update_stats)
    
    def process_new_order(self, order_data: Dict):
        """Traiter une nouvelle commande reçue"""
        try:
            logger.info(f"📦 Nouvelle commande reçue de {order_data.get('user_phone')}")
            
            # Ajouter à la base de données
            order_id = self.data_manager.add_order(
                user_phone=order_data.get('user_phone'),
                user_name=order_data.get('user_name'),
                product_url=order_data.get('product_url'),
                size=order_data.get('size'),
                color=order_data.get('color'),
                quantity=order_data.get('quantity'),
                estimated_price=order_data.get('estimated_price')
            )
            
            if order_id:
                self.stats['orders_added'] += 1
                self.stats['last_activity'] = datetime.now().isoformat()
                
                # Programmer l'ajout automatique au panier (optionnel)
                if Config.AUTO_ADD_TO_CART:
                    self.schedule_cart_addition(order_id)
                
                logger.info(f"✅ Commande {order_id} ajoutée avec succès")
            else:
                logger.error("❌ Échec ajout commande à la base de données")
                self.stats['errors'] += 1
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement nouvelle commande: {e}")
            self.stats['errors'] += 1
    
    def schedule_cart_addition(self, order_id: str):
        """Programmer l'ajout d'une commande au panier Shein"""
        try:
            # Ajouter à la queue de traitement
            threading.Thread(
                target=self.add_to_cart_async,
                args=(order_id,),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"❌ Erreur programmation ajout panier: {e}")
    
    def add_to_cart_async(self, order_id: str):
        """Ajouter une commande au panier de manière asynchrone"""
        try:
            # Attendre un délai pour éviter la surcharge
            time.sleep(Config.CART_ADDITION_DELAY)
            
            # Récupérer les détails de la commande
            orders = self.data_manager.get_all_orders()
            order = next((o for o in orders if o.get('order_id') == order_id), None)
            
            if not order:
                logger.error(f"❌ Commande {order_id} introuvable")
                return
            
            # Ajouter au panier Shein
            success = self.shein_bot.add_product_to_cart(
                product_url=order.get('product_url'),
                size=order.get('size'),
                color=order.get('color'),
                quantity=order.get('quantity')
            )
            
            # Mettre à jour le statut
            if success:
                self.data_manager.update_order_status(order_id, 'completed')
                logger.info(f"✅ Commande {order_id} ajoutée au panier Shein")
            else:
                self.data_manager.update_order_status(order_id, 'failed')
                logger.error(f"❌ Échec ajout commande {order_id} au panier")
                
        except Exception as e:
            logger.error(f"❌ Erreur ajout panier async: {e}")
            self.data_manager.update_order_status(order_id, 'failed')
    
    def update_stats(self, stat_type: str, value: any = 1):
        """Mettre à jour les statistiques"""
        try:
            if stat_type == 'message_processed':
                self.stats['messages_processed'] += value
            elif stat_type == 'error':
                self.stats['errors'] += value
            
            self.stats['last_activity'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour stats: {e}")
    
    def start_whatsapp_listener(self):
        """Démarrer le listener WhatsApp"""
        try:
            logger.info("📱 Démarrage du listener WhatsApp...")
            
            # Démarrer le serveur Flask dans un thread séparé
            whatsapp_thread = threading.Thread(
                target=self.whatsapp_listener.run,
                kwargs={'host': '0.0.0.0', 'port': Config.WHATSAPP_PORT, 'debug': False},
                daemon=True
            )
            whatsapp_thread.start()
            
            logger.info(f"✅ Listener WhatsApp démarré sur le port {Config.WHATSAPP_PORT}")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage listener WhatsApp: {e}")
            raise
    
    def setup_scheduled_tasks(self):
        """Configurer les tâches programmées"""
        try:
            # Traitement automatique des commandes en attente
            schedule.every(Config.AUTO_PROCESS_INTERVAL).minutes.do(self.process_pending_orders)
            
            # Génération automatique de récapitulatifs
            schedule.every().day.at("23:00").do(self.generate_daily_recap)
            
            # Nettoyage des logs anciens
            schedule.every().week.do(self.cleanup_old_logs)
            
            # Sauvegarde des données
            schedule.every(30).minutes.do(self.backup_data)
            
            logger.info("⏰ Tâches programmées configurées")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration tâches programmées: {e}")
    
    def process_pending_orders(self):
        """Traiter les commandes en attente"""
        try:
            logger.info("🔄 Traitement des commandes en attente...")
            
            # Récupérer les commandes en attente
            all_orders = self.data_manager.get_all_orders()
            pending_orders = [o for o in all_orders if o.get('status') == 'pending']
            
            if not pending_orders:
                logger.info("ℹ️ Aucune commande en attente")
                return
            
            logger.info(f"📦 {len(pending_orders)} commandes en attente trouvées")
            
            # Traiter avec le bot Shein
            success_count = self.shein_bot.process_pending_orders()
            
            logger.info(f"✅ {success_count}/{len(pending_orders)} commandes traitées avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement commandes en attente: {e}")
    
    def generate_daily_recap(self):
        """Générer le récapitulatif quotidien"""
        try:
            logger.info("📊 Génération du récapitulatif quotidien...")
            
            # Générer Excel
            excel_path = self.recap_exporter.generate_complete_recap()
            
            # Générer PDF
            pdf_path = self.recap_exporter.generate_pdf_summary()
            
            if excel_path or pdf_path:
                logger.info(f"✅ Récapitulatif généré: Excel={bool(excel_path)}, PDF={bool(pdf_path)}")
            else:
                logger.warning("⚠️ Échec génération récapitulatif")
                
        except Exception as e:
            logger.error(f"❌ Erreur génération récapitulatif quotidien: {e}")
    
    def cleanup_old_logs(self):
        """Nettoyer les anciens logs"""
        try:
            logger.info("🧹 Nettoyage des anciens logs...")
            
            logs_dir = Path(Config.LOGS_DIR)
            if not logs_dir.exists():
                return
            
            # Supprimer les logs de plus de 30 jours
            cutoff_date = datetime.now() - timedelta(days=30)
            
            deleted_count = 0
            for log_file in logs_dir.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    deleted_count += 1
            
            logger.info(f"🗑️ {deleted_count} anciens fichiers de logs supprimés")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage logs: {e}")
    
    def backup_data(self):
        """Sauvegarder les données importantes"""
        try:
            logger.info("💾 Sauvegarde des données...")
            
            # Créer un dossier de sauvegarde
            backup_dir = Path(Config.DATA_DIR) / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Sauvegarder les fichiers principaux
            import shutil
            
            files_to_backup = [
                f"{Config.DATA_DIR}/orders.xlsx",
                f"{Config.DATA_DIR}/users.json"
            ]
            
            for file_path in files_to_backup:
                if Path(file_path).exists():
                    backup_path = backup_dir / f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
                    shutil.copy2(file_path, backup_path)
            
            logger.info(f"✅ Sauvegarde créée dans {backup_dir}")
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
    
    def get_system_status(self) -> Dict:
        """Obtenir le statut du système"""
        try:
            stats = self.data_manager.get_statistics()
            
            return {
                'system': {
                    'running': self.running,
                    'start_time': self.stats.get('start_time'),
                    'uptime': self._calculate_uptime(),
                    'last_activity': self.stats.get('last_activity')
                },
                'performance': {
                    'messages_processed': self.stats.get('messages_processed', 0),
                    'orders_added': self.stats.get('orders_added', 0),
                    'errors': self.stats.get('errors', 0),
                    'success_rate': self._calculate_success_rate()
                },
                'data': stats,
                'components': {
                    'whatsapp_listener': 'running' if self.running else 'stopped',
                    'ai_processor': 'ready',
                    'shein_bot': 'ready',
                    'data_manager': 'ready',
                    'recap_exporter': 'ready'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            return {'error': str(e)}
    
    def _calculate_uptime(self) -> str:
        """Calculer le temps de fonctionnement"""
        if not self.stats.get('start_time'):
            return '0s'
        
        try:
            start = datetime.fromisoformat(self.stats['start_time'])
            uptime = datetime.now() - start
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}j {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m {seconds}s"
                
        except Exception:
            return 'unknown'
    
    def _calculate_success_rate(self) -> float:
        """Calculer le taux de réussite"""
        total = self.stats.get('orders_added', 0) + self.stats.get('errors', 0)
        if total == 0:
            return 100.0
        
        return (self.stats.get('orders_added', 0) / total) * 100
    
    def run_scheduler(self):
        """Exécuter le planificateur de tâches"""
        logger.info("⏰ Démarrage du planificateur de tâches...")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
            except Exception as e:
                logger.error(f"❌ Erreur planificateur: {e}")
                time.sleep(60)
    
    def start(self):
        """Démarrer le système complet"""
        try:
            logger.info("🚀 Démarrage de SHEIN_SEN...")
            
            self.running = True
            self.stats['start_time'] = datetime.now().isoformat()
            
            # Démarrer le listener WhatsApp
            self.start_whatsapp_listener()
            
            # Configurer les tâches programmées
            self.setup_scheduled_tasks()
            
            # Démarrer le planificateur dans un thread séparé
            scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            scheduler_thread.start()
            
            logger.info("✅ SHEIN_SEN démarré avec succès!")
            logger.info(f"📱 WhatsApp Webhook: http://localhost:{Config.WHATSAPP_PORT}/webhook")
            logger.info(f"🔍 Statut: http://localhost:{Config.WHATSAPP_PORT}/status")
            
            # Boucle principale
            self.main_loop()
            
        except KeyboardInterrupt:
            logger.info("⏹️ Arrêt demandé par l'utilisateur")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Erreur critique: {e}")
            self.stop()
            raise
    
    def main_loop(self):
        """Boucle principale du système"""
        logger.info("🔄 Boucle principale démarrée")
        
        try:
            while self.running:
                # Afficher le statut périodiquement
                if int(time.time()) % 300 == 0:  # Toutes les 5 minutes
                    status = self.get_system_status()
                    logger.info(f"📊 Statut: {status['performance']['orders_added']} commandes, {status['performance']['errors']} erreurs")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Interruption clavier détectée")
        except Exception as e:
            logger.error(f"❌ Erreur boucle principale: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Arrêter le système"""
        try:
            logger.info("⏹️ Arrêt de SHEIN_SEN...")
            
            self.running = False
            
            # Sauvegarder les données avant l'arrêt
            self.backup_data()
            
            # Générer un récapitulatif final
            self.generate_daily_recap()
            
            # Afficher les statistiques finales
            final_stats = self.get_system_status()
            logger.info(f"📊 Statistiques finales: {final_stats}")
            
            logger.info("✅ SHEIN_SEN arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt: {e}")

def main():
    """Point d'entrée principal"""
    print("""    
    🛍️ SHEIN_SEN 🛍️
    Système d'Automatisation des Commandes Groupées Shein au Sénégal
    
    Organise, optimise et facilite les commandes Shein collectives.
    """)
    
    try:
        # Créer et démarrer l'orchestrateur
        orchestrator = SheinSenOrchestrator()
        orchestrator.start()
        
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        logger.error(f"Erreur critique dans main: {e}")
    finally:
        print("\n👋 Au revoir!")

if __name__ == "__main__":
    main()