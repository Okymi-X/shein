# 🛍️ SHEIN_SEN

**Système d'Automatisation des Commandes Groupées Shein**

*Organise, optimise et facilite les commandes Shein collectives.*

---

## 📋 Table des Matières

- [🎯 Objectif](#-objectif)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Installation](#️-installation)
- [⚙️ Configuration](#️-configuration)
- [🚀 Utilisation](#-utilisation)
- [📱 Commandes WhatsApp](#-commandes-whatsapp)
- [📊 Récapitulatifs](#-récapitulatifs)
- [🔧 Maintenance](#-maintenance)
- [⚠️ Limitations](#️-limitations)
- [🤝 Contribution](#-contribution)

---

## 🎯 Objectif

SHEIN_SEN automatise la collecte et le traitement des commandes Shein groupées via WhatsApp. Le système :

- ✅ Collecte automatiquement les articles Shein envoyés par WhatsApp
- 🤖 Utilise l'IA pour extraire les détails des produits
- 📊 Organise les données dans des fichiers Excel
- 🛒 Automatise l'ajout au panier Shein (optionnel)
- 📄 Génère des récapitulatifs clairs (Excel/PDF)

---

## ✨ Fonctionnalités

### 📱 Collecte WhatsApp
- Réception automatique des messages via Twilio
- Support des liens produits Shein
- Extraction des tailles, couleurs et quantités
- Gestion multi-utilisateurs

### 🧠 Traitement IA
- Analyse intelligente des messages avec OpenAI GPT-4
- Extraction automatique des informations produit
- Validation et nettoyage des données
- Gestion des erreurs et ambiguïtés

### 💾 Gestion des Données
- Stockage Excel avec multiple feuilles
- Suivi des utilisateurs et statistiques
- Historique complet des commandes
- Sauvegarde automatique

### 🤖 Automatisation Shein
- Navigation automatique avec Playwright
- Gestion des sessions et cookies
- Ajout intelligent au panier
- Gestion des erreurs et retry

### 📊 Récapitulatifs
- Export Excel multi-feuilles
- Génération PDF avec graphiques
- Résumés WhatsApp formatés
- Statistiques détaillées

---

## 🏗️ Architecture

```
/shein_sen/
├── 📁 cookies/              # Sessions Shein (cookies.json)
├── 📁 data/                 # Données Excel/CSV/Logs
│   ├── orders.xlsx          # Base de données des commandes
│   ├── users.json           # Informations utilisateurs
│   └── backups/             # Sauvegardes automatiques
├── 📁 logs/                 # Fichiers de logs
├── 📄 config.py             # Configuration et clés API
├── 📄 whatsapp_listener.py  # Réception messages WhatsApp
├── 📄 ai_processor.py       # Traitement IA des messages
├── 📄 data_manager.py       # Gestion des données
├── 📄 shein_bot.py          # Automatisation Shein
├── 📄 recap_export.py       # Génération récapitulatifs
├── 📄 main.py               # Orchestrateur principal
├── 📄 requirements.txt      # Dépendances Python
└── 📄 README.md             # Documentation
```

---

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Compte Twilio (pour WhatsApp)
- Clé API OpenAI
- Navigateur Chrome/Chromium

### 1. Cloner le projet
```bash
git clone <repository-url>
cd shein_sen
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Installer Playwright
```bash
playwright install chromium
```

### 4. Configuration initiale
```bash
python config.py
```

---

## ⚙️ Configuration

### 1. Variables d'environnement
Créer un fichier `.env` :

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Google Sheets (optionnel)
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
```

### 2. Configuration Twilio
1. Créer un compte sur [Twilio](https://www.twilio.com)
2. Activer WhatsApp Sandbox
3. Configurer le webhook : `https://your-domain.com/webhook`

### 3. Configuration Shein (optionnel)
1. Se connecter à Shein dans Chrome
2. Exporter les cookies vers `cookies/shein_cookies.json`
3. Activer `AUTO_ADD_TO_CART = True` dans `config.py`

---

## 🚀 Utilisation

### Démarrage du système
```bash
python main.py
```

### Vérification du statut
- **Webhook WhatsApp** : `http://localhost:5000/webhook`
- **Statut système** : `http://localhost:5000/status`
- **Statistiques** : `http://localhost:5000/stats`

### Logs en temps réel
```bash
tail -f logs/shein_sen_main.log
```

---

## 📱 Commandes WhatsApp

### Pour les utilisateurs

#### Ajouter un produit
```
https://www.shein.com/fr/item12345
Taille: M
Couleur: Rouge
Quantité: 2
```

#### Commandes disponibles
- `/start` - Démarrer une session
- `/status` - Voir ses commandes
- `/recap` - Récapitulatif personnel
- `/help` - Aide

### Pour l'administrateur
- `/admin_stats` - Statistiques globales
- `/admin_recap` - Récapitulatif complet
- `/admin_process` - Traiter commandes en attente
- `/admin_export` - Générer exports

---

## 📊 Récapitulatifs

### Excel Multi-feuilles
- **Commandes_Détaillées** : Toutes les commandes
- **Résumé_Utilisateurs** : Statistiques par utilisateur
- **Statistiques** : Métriques globales
- **Résumé_Produits** : Groupement par produit
- **Timeline** : Évolution temporelle

### PDF Professionnel
- Statistiques visuelles
- Top utilisateurs
- Commandes récentes
- Graphiques et tableaux

### Exports automatiques
- Récapitulatif quotidien à 23h00
- Sauvegarde toutes les 30 minutes
- Nettoyage logs hebdomadaire

---

## 🔧 Maintenance

### Surveillance
```bash
# Vérifier les logs d'erreurs
tail -f logs/shein_sen_errors.log

# Statistiques système
curl http://localhost:5000/stats

# Redémarrer le service
python main.py
```

### Sauvegarde manuelle
```python
from data_manager import DataManager
from recap_export import RecapExporter

# Sauvegarder données
dm = DataManager()
dm.backup_data()

# Générer récapitulatif
re = RecapExporter()
re.generate_complete_recap()
```

### Nettoyage
```bash
# Nettoyer anciens logs
find logs/ -name "*.log*" -mtime +30 -delete

# Nettoyer anciennes sauvegardes
find data/backups/ -name "*" -mtime +7 -delete
```

---

## ⚠️ Limitations

### Légales
- ⚠️ L'automatisation du panier Shein peut violer les CGU
- 🎓 Usage recommandé : éducatif et personnel uniquement
- 🚫 Ne pas utiliser à grande échelle commerciale

### Techniques
- 🔒 Cookies Shein expiration (reconnexion nécessaire)
- 🌐 Dépendance à la stabilité des APIs externes
- 📱 Limitation Twilio Sandbox (messages pré-approuvés)
- 🤖 Coût des requêtes OpenAI

### Sécurité
- 🔐 Ne jamais partager les cookies de session
- 🔑 Protéger les clés API
- 🛡️ Utiliser HTTPS en production
- 📝 Logs peuvent contenir des données sensibles

---

## 🔧 Dépannage

### Problèmes courants

#### WhatsApp ne reçoit pas les messages
```bash
# Vérifier la configuration Twilio
curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json \
  --data-urlencode "From=whatsapp:+14155238886" \
  --data-urlencode "Body=Test" \
  --data-urlencode "To=whatsapp:+221XXXXXXXXX" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

#### Erreurs OpenAI
```python
# Tester la clé API
import openai
openai.api_key = "your-key"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Test"}],
    max_tokens=10
)
print(response)
```

#### Problèmes Playwright
```bash
# Réinstaller les navigateurs
playwright install --force

# Tester l'installation
playwright open https://www.shein.com
```

---

## 📈 Monitoring

### Métriques importantes
- 📊 Taux de réussite traitement messages
- ⏱️ Temps de réponse moyen
- 🛒 Succès ajout panier Shein
- 💰 Coût API OpenAI
- 📱 Messages WhatsApp traités

### Alertes recommandées
- 🚨 Taux d'erreur > 10%
- ⏰ Pas d'activité > 1 heure
- 💾 Espace disque < 1GB
- 🔑 Expiration cookies Shein

---

## 🤝 Contribution

### Développement
1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

### Standards de code
- Python PEP 8
- Docstrings pour toutes les fonctions
- Tests unitaires pour les nouvelles fonctionnalités
- Logs détaillés pour le debugging

### Tests
```bash
# Tests unitaires
python -m pytest tests/

# Tests d'intégration
python -m pytest tests/integration/

# Coverage
python -m pytest --cov=. tests/
```

---

## 📞 Support

### Documentation
- 📚 Code documenté avec docstrings
- 📝 Logs détaillés dans `/logs/`
- 🔍 Endpoint `/status` pour diagnostics

### Communauté
- 💬 Issues GitHub pour bugs
- 💡 Discussions pour nouvelles fonctionnalités
- 📧 Contact direct pour support urgent

---

## 📄 Licence

**Usage Éducatif et Personnel Uniquement**

Ce projet est destiné à des fins éducatives et personnelles. L'utilisation commerciale ou à grande échelle n'est pas autorisée sans permission explicite.

---

## 🙏 Remerciements

- 🤖 OpenAI pour l'API GPT-4
- 📱 Twilio pour l'intégration WhatsApp
- 🎭 Microsoft Playwright pour l'automatisation
- 🐍 Communauté Python pour les excellentes librairies

---
