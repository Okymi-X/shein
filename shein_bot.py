# -*- coding: utf-8 -*-
"""
SHEIN_SEN - Bot Automatisation Shein
Script Playwright pour automatiser l'ajout de produits au panier Shein
"""

import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger

from config import Config
from data_manager import DataManager

class SheinBot:
    """Bot d'automatisation pour Shein"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.data_manager = DataManager()
        self.setup_logging()
    
    def setup_logging(self):
        """Configuration des logs"""
        logger.add(
            f"{Config.LOGS_DIR}/shein_bot.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
    
    async def initialize_browser(self, headless: bool = None) -> bool:
        """Initialiser le navigateur avec les cookies sauvegardés"""
        try:
            if headless is None:
                headless = Config.BROWSER_HEADLESS
            
            playwright = await async_playwright().start()
            
            # Lancer le navigateur
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Créer un contexte avec user agent réaliste
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='fr-FR'
            )
            
            # Charger les cookies si disponibles
            await self._load_cookies()
            
            # Créer une nouvelle page
            self.page = await self.context.new_page()
            
            # Configuration des timeouts
            self.page.set_default_timeout(Config.BROWSER_TIMEOUT)
            self.page.set_default_navigation_timeout(Config.PAGE_LOAD_TIMEOUT)
            
            logger.info("Navigateur initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation navigateur: {e}")
            return False
    
    async def _load_cookies(self):
        """Charger les cookies sauvegardés"""
        try:
            if Path(Config.COOKIES_FILE).exists():
                with open(Config.COOKIES_FILE, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                await self.context.add_cookies(cookies)
                logger.info(f"Cookies chargés: {len(cookies)} cookies")
            else:
                logger.warning("Aucun fichier de cookies trouvé")
                
        except Exception as e:
            logger.error(f"Erreur chargement cookies: {e}")
    
    async def _save_cookies(self):
        """Sauvegarder les cookies actuels"""
        try:
            if self.context:
                cookies = await self.context.cookies()
                
                with open(Config.COOKIES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, indent=2)
                
                logger.info(f"Cookies sauvegardés: {len(cookies)} cookies")
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde cookies: {e}")
    
    async def check_login_status(self) -> bool:
        """Vérifier si l'utilisateur est connecté"""
        try:
            await self.page.goto(Config.SHEIN_BASE_URL, wait_until='networkidle')
            
            # Attendre que la page se charge
            await asyncio.sleep(3)
            
            # Chercher des indicateurs de connexion
            login_indicators = [
                '[data-testid="user-menu"]',
                '.user-info',
                '[class*="user"][class*="avatar"]',
                'text=Mon compte',
                'text=Profil'
            ]
            
            for indicator in login_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=5000)
                    if element:
                        logger.info("Utilisateur connecté détecté")
                        return True
                except:
                    continue
            
            # Vérifier si on est sur une page de login
            current_url = self.page.url
            if 'login' in current_url.lower():
                logger.warning("Redirection vers page de connexion détectée")
                return False
            
            logger.warning("Statut de connexion incertain")
            return False
            
        except Exception as e:
            logger.error(f"Erreur vérification connexion: {e}")
            return False
    
    async def add_product_to_cart(self, product_url: str, size: str = None, color: str = None, quantity: int = 1) -> Tuple[bool, str]:
        """Ajouter un produit au panier"""
        try:
            logger.info(f"Ajout produit: {product_url} - Taille: {size} - Couleur: {color} - Qté: {quantity}")
            
            # Aller sur la page produit
            await self.page.goto(product_url, wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Vérifier si la page produit est valide
            if not await self._is_valid_product_page():
                return False, "Page produit invalide ou produit non trouvé"
            
            # Sélectionner la taille si spécifiée
            if size:
                size_selected = await self._select_size(size)
                if not size_selected:
                    return False, f"Taille '{size}' non trouvée ou non sélectionnable"
            
            # Sélectionner la couleur si spécifiée
            if color:
                color_selected = await self._select_color(color)
                if not color_selected:
                    logger.warning(f"Couleur '{color}' non trouvée, continuation avec couleur par défaut")
            
            # Ajuster la quantité
            if quantity > 1:
                await self._set_quantity(quantity)
            
            # Ajouter au panier
            add_success = await self._click_add_to_cart()
            if not add_success:
                return False, "Échec ajout au panier - bouton non trouvé ou non cliquable"
            
            # Vérifier le succès
            success_confirmed = await self._confirm_cart_addition()
            
            if success_confirmed:
                logger.info(f"Produit ajouté avec succès: {product_url}")
                return True, "Produit ajouté avec succès"
            else:
                return False, "Ajout au panier non confirmé"
                
        except Exception as e:
            error_msg = f"Erreur ajout produit: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    async def _is_valid_product_page(self) -> bool:
        """Vérifier si on est sur une page produit valide"""
        try:
            # Indicateurs d'une page produit valide
            product_indicators = [
                '[data-testid="product-title"]',
                '.product-intro__head-name',
                '.goods-title',
                'h1[class*="product"]',
                '.product-name'
            ]
            
            for indicator in product_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=5000)
                    if element:
                        return True
                except:
                    continue
            
            # Vérifier l'URL
            current_url = self.page.url
            if '/item' in current_url or '/product' in current_url:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur validation page produit: {e}")
            return False
    
    async def _select_size(self, target_size: str) -> bool:
        """Sélectionner une taille spécifique"""
        try:
            # Sélecteurs possibles pour les tailles
            size_selectors = [
                f'[data-testid="size-{target_size}"]',
                f'button[title="{target_size}"]',
                f'span:has-text("{target_size}"):not([class*="disabled"])',
                f'.size-item:has-text("{target_size}"):not(.disabled)',
                f'[class*="size"]:has-text("{target_size}"):not([class*="disabled"])',
                f'button:has-text("{target_size}"):not([disabled])'
            ]
            
            for selector in size_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        await asyncio.sleep(1)
                        logger.info(f"Taille '{target_size}' sélectionnée")
                        return True
                except:
                    continue
            
            # Méthode alternative: chercher dans tous les éléments contenant la taille
            all_size_elements = await self.page.query_selector_all('[class*="size"], [data-testid*="size"], button, span')
            
            for element in all_size_elements:
                try:
                    text_content = await element.text_content()
                    if text_content and target_size.upper() in text_content.upper():
                        is_disabled = await element.get_attribute('disabled')
                        class_name = await element.get_attribute('class') or ''
                        
                        if not is_disabled and 'disabled' not in class_name.lower():
                            await element.click()
                            await asyncio.sleep(1)
                            logger.info(f"Taille '{target_size}' sélectionnée (méthode alternative)")
                            return True
                except:
                    continue
            
            logger.warning(f"Taille '{target_size}' non trouvée")
            return False
            
        except Exception as e:
            logger.error(f"Erreur sélection taille: {e}")
            return False
    
    async def _select_color(self, target_color: str) -> bool:
        """Sélectionner une couleur spécifique"""
        try:
            # Normaliser la couleur cible
            target_color_lower = target_color.lower()
            
            # Sélecteurs possibles pour les couleurs
            color_selectors = [
                f'[data-testid="color-{target_color}"]',
                f'[title*="{target_color}"]',
                f'[alt*="{target_color}"]',
                f'.color-item:has-text("{target_color}")',
                '[class*="color"], [data-testid*="color"], [class*="swatch"]'
            ]
            
            for selector in color_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    
                    for element in elements:
                        # Vérifier le titre, alt, ou contenu textuel
                        title = await element.get_attribute('title') or ''
                        alt = await element.get_attribute('alt') or ''
                        text = await element.text_content() or ''
                        
                        if (target_color_lower in title.lower() or 
                            target_color_lower in alt.lower() or 
                            target_color_lower in text.lower()):
                            
                            await element.click()
                            await asyncio.sleep(1)
                            logger.info(f"Couleur '{target_color}' sélectionnée")
                            return True
                            
                except:
                    continue
            
            logger.warning(f"Couleur '{target_color}' non trouvée")
            return False
            
        except Exception as e:
            logger.error(f"Erreur sélection couleur: {e}")
            return False
    
    async def _set_quantity(self, quantity: int) -> bool:
        """Définir la quantité"""
        try:
            # Sélecteurs possibles pour la quantité
            qty_selectors = [
                '[data-testid="quantity-input"]',
                'input[name="quantity"]',
                'input[class*="quantity"]',
                '.quantity-input input',
                '[class*="qty"] input'
            ]
            
            for selector in qty_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        # Effacer et saisir la nouvelle quantité
                        await element.click()
                        await element.fill('')
                        await element.type(str(quantity))
                        await asyncio.sleep(1)
                        logger.info(f"Quantité définie: {quantity}")
                        return True
                except:
                    continue
            
            # Méthode alternative: utiliser les boutons +/-
            plus_button_selectors = [
                '[data-testid="quantity-plus"]',
                'button[class*="plus"]',
                'button:has-text("+")',
                '.quantity-plus'
            ]
            
            for selector in plus_button_selectors:
                try:
                    plus_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if plus_button:
                        # Cliquer quantity-1 fois sur le bouton +
                        for _ in range(quantity - 1):
                            await plus_button.click()
                            await asyncio.sleep(0.5)
                        
                        logger.info(f"Quantité définie via boutons: {quantity}")
                        return True
                except:
                    continue
            
            logger.warning(f"Impossible de définir la quantité: {quantity}")
            return False
            
        except Exception as e:
            logger.error(f"Erreur définition quantité: {e}")
            return False
    
    async def _click_add_to_cart(self) -> bool:
        """Cliquer sur le bouton d'ajout au panier"""
        try:
            # Sélecteurs possibles pour le bouton d'ajout
            add_to_cart_selectors = [
                '[data-testid="add-to-cart"]',
                'button:has-text("Ajouter au panier")',
                'button:has-text("Add to cart")',
                'button:has-text("AJOUTER")',
                '.add-to-cart-btn',
                '[class*="add-cart"]',
                'button[class*="cart"]'
            ]
            
            for selector in add_to_cart_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        # Vérifier si le bouton est cliquable
                        is_disabled = await element.get_attribute('disabled')
                        if not is_disabled:
                            await element.click()
                            await asyncio.sleep(2)
                            logger.info("Bouton 'Ajouter au panier' cliqué")
                            return True
                except:
                    continue
            
            logger.error("Bouton 'Ajouter au panier' non trouvé")
            return False
            
        except Exception as e:
            logger.error(f"Erreur clic ajout panier: {e}")
            return False
    
    async def _confirm_cart_addition(self) -> bool:
        """Confirmer que le produit a été ajouté au panier"""
        try:
            # Indicateurs de succès
            success_indicators = [
                'text=Ajouté au panier',
                'text=Added to cart',
                'text=Produit ajouté',
                '[data-testid="cart-success"]',
                '.success-message',
                '[class*="success"]'
            ]
            
            for indicator in success_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=5000)
                    if element:
                        logger.info("Confirmation d'ajout au panier reçue")
                        return True
                except:
                    continue
            
            # Vérifier si une popup ou modal s'est ouverte
            modal_selectors = [
                '[role="dialog"]',
                '.modal',
                '.popup',
                '[class*="overlay"]'
            ]
            
            for selector in modal_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        logger.info("Modal/popup détectée - probablement ajout réussi")
                        return True
                except:
                    continue
            
            # Attendre un peu et considérer comme succès si pas d'erreur
            await asyncio.sleep(3)
            logger.info("Pas de confirmation explicite, mais pas d'erreur détectée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur confirmation ajout: {e}")
            return False
    
    async def process_pending_orders(self) -> Dict[str, int]:
        """Traiter toutes les commandes en attente"""
        try:
            pending_orders = self.data_manager.get_all_orders(status='pending')
            
            if not pending_orders:
                logger.info("Aucune commande en attente")
                return {'success': 0, 'failed': 0, 'total': 0}
            
            logger.info(f"Traitement de {len(pending_orders)} commandes en attente")
            
            results = {'success': 0, 'failed': 0, 'total': len(pending_orders)}
            
            for order in pending_orders:
                try:
                    order_id = order.get('order_id')
                    product_url = order.get('product_url')
                    size = order.get('size')
                    color = order.get('color')
                    quantity = order.get('quantity', 1)
                    
                    logger.info(f"Traitement commande: {order_id}")
                    
                    # Ajouter le produit au panier
                    success, message = await self.add_product_to_cart(
                        product_url, size, color, quantity
                    )
                    
                    if success:
                        # Mettre à jour le statut
                        self.data_manager.update_order_status(
                            order_id, 'completed', 'Ajouté automatiquement au panier'
                        )
                        results['success'] += 1
                        logger.info(f"Commande {order_id} traitée avec succès")
                    else:
                        # Marquer comme échouée
                        self.data_manager.update_order_status(
                            order_id, 'failed', f'Erreur: {message}'
                        )
                        results['failed'] += 1
                        logger.error(f"Échec commande {order_id}: {message}")
                    
                    # Délai entre les commandes
                    await asyncio.sleep(Config.RATE_LIMIT_DELAY)
                    
                except Exception as e:
                    logger.error(f"Erreur traitement commande {order.get('order_id', 'Unknown')}: {e}")
                    results['failed'] += 1
            
            logger.info(f"Traitement terminé: {results['success']} succès, {results['failed']} échecs")
            return results
            
        except Exception as e:
            logger.error(f"Erreur traitement commandes: {e}")
            return {'success': 0, 'failed': 0, 'total': 0}
    
    async def close(self):
        """Fermer le navigateur et sauvegarder les cookies"""
        try:
            if self.context:
                await self._save_cookies()
            
            if self.browser:
                await self.browser.close()
            
            logger.info("Navigateur fermé")
            
        except Exception as e:
            logger.error(f"Erreur fermeture navigateur: {e}")

# Fonction utilitaire pour exécution standalone
async def run_shein_bot():
    """Exécuter le bot Shein de manière autonome"""
    bot = SheinBot()
    
    try:
        # Initialiser le navigateur
        if not await bot.initialize_browser():
            logger.error("Échec initialisation navigateur")
            return
        
        # Vérifier la connexion
        if not await bot.check_login_status():
            logger.warning("Utilisateur non connecté - connexion manuelle requise")
            input("Veuillez vous connecter manuellement sur Shein, puis appuyez sur Entrée...")
        
        # Traiter les commandes en attente
        results = await bot.process_pending_orders()
        
        print(f"\n📊 Résultats du traitement:")
        print(f"✅ Succès: {results['success']}")
        print(f"❌ Échecs: {results['failed']}")
        print(f"📋 Total: {results['total']}")
        
    except Exception as e:
        logger.error(f"Erreur exécution bot: {e}")
    
    finally:
        await bot.close()

# Point d'entrée
if __name__ == "__main__":
    asyncio.run(run_shein_bot())