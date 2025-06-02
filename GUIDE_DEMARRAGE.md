# 🚀 Guide de Démarrage Rapide - SHEIN_SEN

## 📋 Prérequis

### 1. Python 3.8+
- **Windows**: Téléchargez depuis [python.org](https://www.python.org/downloads/)
- **Vérification**: Ouvrez un terminal et tapez `python --version`

### 2. Comptes requis
- **OpenAI**: [Créer un compte](https://platform.openai.com/) et obtenir une clé API
- **Twilio**: [Créer un compte](https://www.twilio.com/) pour WhatsApp API
- **Google Chrome**: Requis pour l'automatisation Shein

## ⚡ Installation Express (3 minutes)

### Étape 1: Télécharger le projet
```bash
# Si vous avez git
git clone <url-du-projet>
cd Shein_Sen

# Ou téléchargez et décompressez le ZIP
```

### Étape 2: Configuration automatique
```bash
# Exécutez le script de configuration
python setup.py
```

Le script va:
- ✅ Installer toutes les dépendances
- ✅ Créer les dossiers nécessaires
- ✅ Configurer l'environnement
- ✅ Vous guider pour les clés API

### Étape 3: Configuration des clés API

Éditez le fichier `.env` avec vos vraies clés:

```env
# OpenAI (OBLIGATOIRE)
OPENAI_API_KEY=sk-votre-cle-openai-ici

# Twilio WhatsApp (OBLIGATOIRE)
TWILIO_ACCOUNT_SID=votre-account-sid
TWILIO_AUTH_TOKEN=votre-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Admin WhatsApp (OBLIGATOIRE)
ADMIN_WHATSAPP_NUMBER=whatsapp:+221XXXXXXXXX
```

## 🚀 Démarrage

### Option 1: Script automatique (Windows)
```bash
# Double-cliquez sur start.bat
# OU dans le terminal:
start.bat
```

### Option 2: Manuel
```bash
python main.py
```

### Option 3: Test du système
```bash
# Tester tous les composants
python test_system.py
```

## 📱 Configuration WhatsApp

### 1. Twilio Sandbox
1. Allez sur [Twilio Console](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Notez votre numéro sandbox (ex: `whatsapp:+14155238886`)
3. Configurez le webhook: `https://votre-domaine.com/webhook`

### 2. Test local avec ngrok
```bash
# Installer ngrok
npm install -g ngrok
# OU télécharger depuis ngrok.com

# Exposer le port local
ngrok http 5000

# Utiliser l'URL ngrok comme webhook
# Ex: https://abc123.ngrok.io/webhook
```

## 🧪 Test du Système

### 1. Vérifier le statut
Ouvrez dans votre navigateur: `http://localhost:5000/status`

### 2. Test WhatsApp
Envoyez un message à votre numéro Twilio:
```
https://www.shein.com/fr/item12345 - Taille M - Couleur Rouge - Quantité 2
```

### 3. Commandes disponibles
- `/start` - Commencer
- `/status` - Statut de vos commandes
- `/recap` - Récapitulatif personnel
- `/help` - Aide

## 📊 Interface Web

### Endpoints disponibles:
- `http://localhost:5000/` - Page d'accueil
- `http://localhost:5000/status` - Statut du système
- `http://localhost:5000/webhook` - Webhook WhatsApp
- `http://localhost:5000/stats` - Statistiques
- `http://localhost:5000/admin/recap` - Récapitulatif admin

## 🔧 Configuration Avancée

### Variables d'environnement importantes:

```env
# Limites
MAX_ITEMS_PER_USER=10
MAX_ITEMS_PER_DAY=50

# Automatisation Shein
AUTO_ADD_TO_CART=true
SHEIN_DELAY_BETWEEN_ACTIONS=2

# IA
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=500

# Sécurité
VALIDATE_SHEIN_URLS=true
ALLOW_EXTERNAL_URLS=false
```

## 📁 Structure des Fichiers

```
Shein_Sen/
├── 📄 main.py              # Point d'entrée principal
├── 📄 config.py            # Configuration
├── 📄 whatsapp_listener.py # Réception WhatsApp
├── 📄 ai_processor.py      # Traitement IA
├── 📄 shein_bot.py         # Automatisation Shein
├── 📄 data_manager.py      # Gestion des données
├── 📄 recap_export.py      # Export Excel/PDF
├── 📄 setup.py             # Script d'installation
├── 📄 test_system.py       # Tests du système
├── 📄 start.bat            # Démarrage Windows
├── 📁 data/                # Données (Excel, JSON)
├── 📁 logs/                # Fichiers de log
├── 📁 cookies/             # Cookies Shein
└── 📁 backups/             # Sauvegardes
```

## 🛠️ Dépannage

### Problèmes courants:

#### ❌ "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

#### ❌ "OpenAI API Error"
- Vérifiez votre clé API dans `.env`
- Vérifiez votre crédit OpenAI
- Testez avec: `python -c "import openai; print('OK')"`

#### ❌ "Twilio Error"
- Vérifiez vos identifiants Twilio
- Vérifiez que le webhook est configuré
- Testez avec ngrok pour le développement local

#### ❌ "Playwright Error"
```bash
# Réinstaller les navigateurs
python -m playwright install chromium
```

#### ❌ "Permission Denied"
- Exécutez en tant qu'administrateur (Windows)
- Vérifiez les permissions des dossiers

### Logs utiles:
- `logs/shein_sen.log` - Log principal
- `logs/whatsapp.log` - Messages WhatsApp
- `logs/shein_bot.log` - Automatisation Shein
- `logs/test_report_*.json` - Rapports de test

## 📈 Monitoring

### Métriques disponibles:
- Nombre de commandes traitées
- Taux de succès d'ajout au panier
- Temps de réponse moyen
- Erreurs par composant

### Alertes automatiques:
- Échec d'ajout au panier
- Erreurs API répétées
- Limite d'utilisateur atteinte
- Problème de connexion Shein

## 🔒 Sécurité

### Bonnes pratiques:
- ✅ Ne jamais partager vos clés API
- ✅ Utiliser HTTPS en production
- ✅ Limiter l'accès aux webhooks
- ✅ Sauvegarder régulièrement les données
- ✅ Surveiller les logs d'erreur

### Limitations légales:
- ⚠️ Usage personnel/éducatif uniquement
- ⚠️ Respecter les CGU de Shein
- ⚠️ Ne pas utiliser à grande échelle

## 🆘 Support

### En cas de problème:
1. 📋 Consultez les logs dans `logs/`
2. 🧪 Exécutez `python test_system.py`
3. 📖 Relisez ce guide
4. 🔍 Vérifiez la configuration dans `.env`
5. 🌐 Testez la connectivité internet

### Ressources utiles:
- [Documentation Twilio WhatsApp](https://www.twilio.com/docs/whatsapp)
- [Documentation OpenAI](https://platform.openai.com/docs)
- [Documentation Playwright](https://playwright.dev/python/)

## 🎯 Prochaines Étapes

Après l'installation:
1. ✅ Testez avec un message WhatsApp
2. ✅ Vérifiez l'ajout au panier Shein
3. ✅ Générez votre premier récapitulatif
4. ✅ Configurez les sauvegardes automatiques
5. ✅ Invitez vos utilisateurs à tester

---

**🎉 Félicitations! SHEIN_SEN est maintenant opérationnel!**

*Pour toute question, consultez les logs ou relancez `python test_system.py`*