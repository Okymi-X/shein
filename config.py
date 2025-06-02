# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Configuration
Système d'Automatisation des Commandes Groupées Shein au Sénégal
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration principale du système SHEIN_SEN"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    # Google Sheets (optionnel)
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', '')
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID', '')
    
    # Chemins des fichiers
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    COOKIES_DIR = os.path.join(BASE_DIR, 'cookies')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Fichiers de données
    ORDERS_FILE = os.path.join(DATA_DIR, 'commandes_shein.xlsx')
    USERS_FILE = os.path.join(DATA_DIR, 'utilisateurs.json')
    COOKIES_FILE = os.path.join(COOKIES_DIR, 'shein_cookies.json')
    
    # Configuration Shein
    SHEIN_BASE_URL = 'https://www.shein.com/fr/'
    SHEIN_CART_URL = 'https://www.shein.com/fr/cart'
    SHEIN_LOGIN_URL = 'https://www.shein.com/fr/user/login'
    
    # Configuration Playwright
    BROWSER_HEADLESS = True
    BROWSER_TIMEOUT = 30000  # 30 secondes
    PAGE_LOAD_TIMEOUT = 15000  # 15 secondes
    
    # Configuration IA
    AI_MODEL = 'gpt-4'
    AI_TEMPERATURE = 0.1
    AI_MAX_TOKENS = 500
    
    # Limites et sécurité
    MAX_ITEMS_PER_USER = 20
    MAX_TOTAL_ITEMS = 100
    RATE_LIMIT_DELAY = 2  # secondes entre les requêtes
    
    # Messages WhatsApp
    WELCOME_MESSAGE = """🛍️ Bienvenue sur SHEIN_SEN!
    
Envoyez vos articles Shein sous ce format:
📱 Lien du produit
📏 Taille: M
🎨 Couleur: Rouge
📦 Quantité: 2

Exemple:
https://www.shein.com/fr/item12345
Taille: M
Couleur: Rouge
Quantité: 1"""
    
    ERROR_MESSAGE = "❌ Format incorrect. Veuillez envoyer le lien Shein avec taille, couleur et quantité."
    SUCCESS_MESSAGE = "✅ Article ajouté avec succès!"
    
    @classmethod
    def create_directories(cls):
        """Créer les dossiers nécessaires"""
        directories = [cls.DATA_DIR, cls.COOKIES_DIR, cls.LOGS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Valider la configuration"""
        required_keys = ['OPENAI_API_KEY', 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']
        missing_keys = []
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Clés de configuration manquantes: {', '.join(missing_keys)}")
        
        return True

# Créer les dossiers au démarrage
Config.create_directories()