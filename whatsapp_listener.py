# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Écouteur WhatsApp
Réception et traitement des messages WhatsApp via Twilio
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from loguru import logger

from config import Config
from ai_processor import AIProcessor
from data_manager import DataManager

class WhatsAppListener:
    """Gestionnaire des messages WhatsApp entrants"""
    
    def __init__(self):
        self.twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.ai_processor = AIProcessor()
        self.data_manager = DataManager()
        self.app = Flask(__name__)
        self.setup_logging()
        self.setup_routes()
    
    def setup_logging(self):
        """Configuration des logs"""
        logger.add(
            f"{Config.LOGS_DIR}/whatsapp_listener.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
    
    def setup_routes(self):
        """Configuration des routes Flask"""
        
        @self.app.route('/webhook/whatsapp', methods=['POST'])
        def whatsapp_webhook():
            """Webhook pour recevoir les messages WhatsApp"""
            try:
                # Récupérer les données du message
                message_data = {
                    'from': request.form.get('From', ''),
                    'to': request.form.get('To', ''),
                    'body': request.form.get('Body', ''),
                    'message_sid': request.form.get('MessageSid', ''),
                    'account_sid': request.form.get('AccountSid', ''),
                    'received_at': datetime.now().isoformat()
                }
                
                logger.info(f"Message reçu de {message_data['from']}: {message_data['body'][:100]}")
                
                # Traiter le message
                response_message = self.process_incoming_message(message_data)
                
                # Créer la réponse Twilio
                twiml_response = MessagingResponse()
                twiml_response.message(response_message)
                
                return str(twiml_response)
                
            except Exception as e:
                logger.error(f"Erreur webhook WhatsApp: {e}")
                twiml_response = MessagingResponse()
                twiml_response.message(Config.ERROR_MESSAGE)
                return str(twiml_response)
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Vérification de santé du service"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'SHEIN_SEN WhatsApp Listener'
            })
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Statistiques du service"""
            try:
                stats = self.data_manager.get_statistics()
                return jsonify(stats)
            except Exception as e:
                logger.error(f"Erreur récupération stats: {e}")
                return jsonify({'error': 'Erreur récupération statistiques'}), 500
    
    def process_incoming_message(self, message_data: Dict) -> str:
        """Traiter un message WhatsApp entrant"""
        try:
            user_phone = self._clean_phone_number(message_data['from'])
            message_body = message_data['body'].strip()
            
            # Vérifier si c'est un message de commande
            if message_body.lower() in ['/start', '/aide', '/help']:
                return Config.WELCOME_MESSAGE
            
            if message_body.lower() in ['/status', '/statut']:
                return self._get_user_status(user_phone)
            
            if message_body.lower() in ['/recap', '/résumé']:
                return self._get_user_summary(user_phone)
            
            # Traiter comme une commande produit
            return self._process_product_message(message_body, user_phone, message_data)
            
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            return Config.ERROR_MESSAGE
    
    def _process_product_message(self, message: str, user_phone: str, message_data: Dict) -> str:
        """Traiter un message contenant des informations produit"""
        try:
            # Extraire les informations avec l'IA
            extracted_data = self.ai_processor.extract_product_info(message, user_phone)
            
            if not extracted_data or not extracted_data.get('product_url'):
                return f"{Config.ERROR_MESSAGE}\n\n{Config.WELCOME_MESSAGE}"
            
            # Vérifier les limites utilisateur
            user_orders = self.data_manager.get_user_orders(user_phone)
            if len(user_orders) >= Config.MAX_ITEMS_PER_USER:
                return f"❌ Limite atteinte: maximum {Config.MAX_ITEMS_PER_USER} articles par utilisateur."
            
            # Ajouter les métadonnées
            extracted_data.update({
                'message_sid': message_data.get('message_sid'),
                'raw_message': message,
                'processed_at': datetime.now().isoformat()
            })
            
            # Sauvegarder la commande
            order_id = self.data_manager.add_order(extracted_data)
            
            if order_id:
                # Créer le message de confirmation
                confirmation = self._create_confirmation_message(extracted_data, order_id)
                
                # Log de succès
                logger.info(f"Commande ajoutée - ID: {order_id}, User: {user_phone}")
                
                return confirmation
            else:
                return "❌ Erreur lors de l'enregistrement. Veuillez réessayer."
                
        except Exception as e:
            logger.error(f"Erreur traitement produit: {e}")
            return Config.ERROR_MESSAGE
    
    def _create_confirmation_message(self, data: Dict, order_id: str) -> str:
        """Créer un message de confirmation détaillé"""
        message_parts = [
            "✅ Article ajouté avec succès!",
            f"📋 ID Commande: {order_id}",
            "",
            "📦 Détails:"
        ]
        
        if data.get('size'):
            message_parts.append(f"📏 Taille: {data['size']}")
        
        if data.get('color'):
            message_parts.append(f"🎨 Couleur: {data['color']}")
        
        message_parts.append(f"📊 Quantité: {data.get('quantity', 1)}")
        
        message_parts.extend([
            "",
            "💡 Commandes disponibles:",
            "• /status - Voir vos commandes",
            "• /recap - Résumé complet",
            "• /aide - Aide"
        ])
        
        return "\n".join(message_parts)
    
    def _get_user_status(self, user_phone: str) -> str:
        """Obtenir le statut des commandes d'un utilisateur"""
        try:
            orders = self.data_manager.get_user_orders(user_phone)
            
            if not orders:
                return "📋 Aucune commande trouvée.\n\n" + Config.WELCOME_MESSAGE
            
            message_parts = [
                f"📋 Vos commandes ({len(orders)}/{Config.MAX_ITEMS_PER_USER}):",
                ""
            ]
            
            total_items = 0
            for i, order in enumerate(orders[-5:], 1):  # Dernières 5 commandes
                status_emoji = "⏳" if order.get('status') == 'pending' else "✅"
                size_info = f" - {order.get('size')}" if order.get('size') else ""
                color_info = f" - {order.get('color')}" if order.get('color') else ""
                qty = order.get('quantity', 1)
                total_items += qty
                
                message_parts.append(
                    f"{status_emoji} {i}. Qté: {qty}{size_info}{color_info}"
                )
            
            if len(orders) > 5:
                message_parts.append(f"... et {len(orders) - 5} autres")
            
            message_parts.extend([
                "",
                f"📊 Total articles: {total_items}",
                "💡 /recap pour le résumé complet"
            ])
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Erreur statut utilisateur: {e}")
            return "❌ Erreur lors de la récupération du statut."
    
    def _get_user_summary(self, user_phone: str) -> str:
        """Obtenir un résumé complet pour l'utilisateur"""
        try:
            summary = self.data_manager.generate_user_summary(user_phone)
            
            if not summary:
                return "📋 Aucune commande trouvée."
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur résumé utilisateur: {e}")
            return "❌ Erreur lors de la génération du résumé."
    
    def _clean_phone_number(self, phone: str) -> str:
        """Nettoyer et normaliser le numéro de téléphone"""
        # Supprimer le préfixe WhatsApp
        if phone.startswith('whatsapp:'):
            phone = phone.replace('whatsapp:', '')
        
        # Normaliser le format
        phone = phone.strip().replace(' ', '').replace('-', '')
        
        return phone
    
    def send_message(self, to_phone: str, message: str) -> bool:
        """Envoyer un message WhatsApp"""
        try:
            # Ajouter le préfixe WhatsApp si nécessaire
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            message_instance = self.twilio_client.messages.create(
                body=message,
                from_=Config.TWILIO_WHATSAPP_NUMBER,
                to=to_phone
            )
            
            logger.info(f"Message envoyé à {to_phone}: {message_instance.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}")
            return False
    
    def broadcast_message(self, phone_numbers: List[str], message: str) -> Dict:
        """Envoyer un message à plusieurs utilisateurs"""
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for phone in phone_numbers:
            if self.send_message(phone, message):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(phone)
            
            # Délai pour éviter le rate limiting
            time.sleep(1)
        
        logger.info(f"Broadcast terminé: {results['success']} succès, {results['failed']} échecs")
        return results
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Démarrer le serveur Flask"""
        logger.info(f"Démarrage WhatsApp Listener sur {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Point d'entrée pour le serveur
if __name__ == "__main__":
    try:
        # Valider la configuration
        Config.validate_config()
        
        # Créer et démarrer le listener
        listener = WhatsAppListener()
        listener.run(debug=True)
        
    except Exception as e:
        logger.error(f"Erreur démarrage: {e}")
        print(f"❌ Erreur: {e}")