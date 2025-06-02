# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Processeur IA
Traitement intelligent des messages WhatsApp pour extraire les informations produits
"""

import re
import json
import openai
from typing import Dict, Optional, List
from loguru import logger
from config import Config
import validators

class AIProcessor:
    """Processeur IA pour analyser les messages WhatsApp et extraire les données produits"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.setup_logging()
    
    def setup_logging(self):
        """Configuration des logs"""
        logger.add(
            f"{Config.LOGS_DIR}/ai_processor.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
    
    def extract_product_info(self, message: str, user_phone: str = None) -> Optional[Dict]:
        """
        Extraire les informations produit d'un message WhatsApp
        
        Args:
            message: Message WhatsApp reçu
            user_phone: Numéro de téléphone de l'utilisateur
            
        Returns:
            Dict avec les informations extraites ou None si échec
        """
        try:
            # Pré-traitement du message
            cleaned_message = self._clean_message(message)
            
            # Extraction basique avec regex
            basic_info = self._extract_with_regex(cleaned_message)
            
            # Si l'extraction basique échoue, utiliser l'IA
            if not basic_info.get('product_url'):
                ai_info = self._extract_with_ai(cleaned_message)
                if ai_info:
                    basic_info.update(ai_info)
            
            # Validation et nettoyage final
            if basic_info.get('product_url'):
                result = self._validate_and_clean(basic_info, user_phone)
                logger.info(f"Extraction réussie pour {user_phone}: {result}")
                return result
            
            logger.warning(f"Échec extraction pour {user_phone}: {message[:100]}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur extraction IA: {e}")
            return None
    
    def _clean_message(self, message: str) -> str:
        """Nettoyer et normaliser le message"""
        # Supprimer les caractères spéciaux et normaliser
        cleaned = re.sub(r'[\n\r\t]+', ' ', message)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Normaliser les termes courants
        replacements = {
            'taille': 'Taille',
            'couleur': 'Couleur',
            'quantité': 'Quantité',
            'quantite': 'Quantité',
            'qte': 'Quantité',
            'color': 'Couleur',
            'size': 'Taille',
            'qty': 'Quantité'
        }
        
        for old, new in replacements.items():
            cleaned = re.sub(rf'\b{old}\b', new, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _extract_with_regex(self, message: str) -> Dict:
        """Extraction basique avec expressions régulières"""
        result = {
            'product_url': None,
            'size': None,
            'color': None,
            'quantity': 1
        }
        
        # Extraction URL Shein
        url_pattern = r'https?://(?:www\.)?shein\.com/[^\s]+'
        url_match = re.search(url_pattern, message, re.IGNORECASE)
        if url_match:
            result['product_url'] = url_match.group(0)
        
        # Extraction taille
        size_patterns = [
            r'Taille\s*:?\s*([A-Z]{1,3}|\d+)',
            r'Size\s*:?\s*([A-Z]{1,3}|\d+)',
            r'\b([XS|S|M|L|XL|XXL|XXXL])\b'
        ]
        
        for pattern in size_patterns:
            size_match = re.search(pattern, message, re.IGNORECASE)
            if size_match:
                result['size'] = size_match.group(1).upper()
                break
        
        # Extraction couleur
        color_patterns = [
            r'Couleur\s*:?\s*([A-Za-zÀ-ÿ\s]+?)(?:\s|$|\n)',
            r'Color\s*:?\s*([A-Za-zÀ-ÿ\s]+?)(?:\s|$|\n)'
        ]
        
        for pattern in color_patterns:
            color_match = re.search(pattern, message, re.IGNORECASE)
            if color_match:
                result['color'] = color_match.group(1).strip().title()
                break
        
        # Extraction quantité
        qty_patterns = [
            r'Quantité\s*:?\s*(\d+)',
            r'Qty\s*:?\s*(\d+)',
            r'\b(\d+)\s*pièces?\b'
        ]
        
        for pattern in qty_patterns:
            qty_match = re.search(pattern, message, re.IGNORECASE)
            if qty_match:
                result['quantity'] = int(qty_match.group(1))
                break
        
        return result
    
    def _extract_with_ai(self, message: str) -> Optional[Dict]:
        """Extraction avancée avec IA GPT"""
        try:
            prompt = f"""
            Analyse ce message WhatsApp et extrait les informations produit Shein.
            
            Message: "{message}"
            
            Retourne UNIQUEMENT un JSON valide avec ces champs:
            {{
                "product_url": "URL du produit Shein (ou null)",
                "size": "Taille (S, M, L, XL, etc. ou null)",
                "color": "Couleur (ou null)",
                "quantity": nombre (défaut: 1)
            }}
            
            Règles:
            - URL doit contenir "shein.com"
            - Taille en majuscules (S, M, L, XL, XXL, etc.)
            - Couleur en français, première lettre majuscule
            - Quantité doit être un nombre entier
            - Si une info manque, mettre null
            """
            
            response = self.client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "Tu es un assistant spécialisé dans l'extraction d'informations produits e-commerce. Réponds uniquement en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.AI_MAX_TOKENS
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Nettoyer la réponse (supprimer markdown si présent)
            if ai_response.startswith('```'):
                ai_response = re.sub(r'^```(?:json)?\n?', '', ai_response)
                ai_response = re.sub(r'\n?```$', '', ai_response)
            
            # Parser le JSON
            result = json.loads(ai_response)
            
            logger.info(f"Extraction IA réussie: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON IA: {e} - Réponse: {ai_response}")
            return None
        except Exception as e:
            logger.error(f"Erreur IA: {e}")
            return None
    
    def _validate_and_clean(self, data: Dict, user_phone: str = None) -> Dict:
        """Valider et nettoyer les données extraites"""
        result = {
            'user_phone': user_phone,
            'product_url': None,
            'size': None,
            'color': None,
            'quantity': 1,
            'status': 'pending',
            'extracted_at': None
        }
        
        # Validation URL
        if data.get('product_url'):
            url = data['product_url'].strip()
            if validators.url(url) and 'shein.com' in url.lower():
                result['product_url'] = url
        
        # Validation taille
        if data.get('size'):
            size = str(data['size']).strip().upper()
            valid_sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
            # Accepter aussi les tailles numériques
            if size in valid_sizes or re.match(r'^\d+$', size):
                result['size'] = size
        
        # Validation couleur
        if data.get('color'):
            color = str(data['color']).strip().title()
            if len(color) <= 50:  # Limite raisonnable
                result['color'] = color
        
        # Validation quantité
        try:
            qty = int(data.get('quantity', 1))
            if 1 <= qty <= Config.MAX_ITEMS_PER_USER:
                result['quantity'] = qty
        except (ValueError, TypeError):
            result['quantity'] = 1
        
        # Timestamp
        from datetime import datetime
        result['extracted_at'] = datetime.now().isoformat()
        
        return result
    
    def batch_process(self, messages: List[Dict]) -> List[Dict]:
        """Traiter plusieurs messages en lot"""
        results = []
        
        for msg_data in messages:
            message = msg_data.get('message', '')
            user_phone = msg_data.get('user_phone')
            
            extracted = self.extract_product_info(message, user_phone)
            if extracted:
                results.append(extracted)
        
        logger.info(f"Traitement lot: {len(results)}/{len(messages)} réussis")
        return results

# Test unitaire
if __name__ == "__main__":
    # Test basique
    processor = AIProcessor()
    
    test_message = """
    https://www.shein.com/fr/item12345
    Taille: M
    Couleur: Rouge
    Quantité: 2
    """
    
    result = processor.extract_product_info(test_message, "+221701234567")
    print("Résultat test:", json.dumps(result, indent=2, ensure_ascii=False))