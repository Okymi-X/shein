# 📡 Documentation API - SHEIN_SEN

## 🌐 Vue d'ensemble

SHEIN_SEN expose plusieurs endpoints REST pour l'intégration et le monitoring du système.

**Base URL**: `http://localhost:5000` (développement)

## 🔗 Endpoints Disponibles

### 1. 🏠 Page d'accueil
```http
GET /
```

**Description**: Page d'accueil avec informations système

**Réponse**:
```json
{
  "service": "SHEIN_SEN",
  "version": "1.0.0",
  "status": "running",
  "description": "Système d'Automatisation des Commandes Groupées Shein"
}
```

### 2. 📊 Statut du système
```http
GET /status
```

**Description**: Statut détaillé de tous les composants

**Réponse**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "whatsapp_listener": "active",
    "ai_processor": "ready",
    "shein_bot": "standby",
    "data_manager": "operational",
    "recap_exporter": "ready"
  },
  "statistics": {
    "total_orders": 45,
    "pending_orders": 3,
    "completed_orders": 40,
    "failed_orders": 2,
    "active_users": 12
  },
  "performance": {
    "avg_processing_time": 2.3,
    "success_rate": 95.5,
    "uptime": "2 days, 14 hours"
  }
}
```

### 3. 📱 Webhook WhatsApp
```http
POST /webhook
```

**Description**: Endpoint pour recevoir les messages WhatsApp de Twilio

**Headers requis**:
```
Content-Type: application/x-www-form-urlencoded
```

**Paramètres (form-data)**:
- `From`: Numéro WhatsApp de l'expéditeur (ex: `whatsapp:+221701234567`)
- `To`: Numéro WhatsApp de destination (ex: `whatsapp:+14155238886`)
- `Body`: Contenu du message
- `MessageSid`: ID unique du message Twilio
- `AccountSid`: SID du compte Twilio

**Exemple de payload**:
```
From=whatsapp%3A%2B221701234567
To=whatsapp%3A%2B14155238886
Body=https%3A//www.shein.com/fr/item12345%20-%20Taille%20M%20-%20Couleur%20Rouge
MessageSid=SM1234567890abcdef
AccountSid=AC1234567890abcdef
```

**Réponse succès**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>✅ Produit ajouté avec succès! Merci Awa.</Message>
</Response>
```

**Réponse erreur**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>❌ Erreur: URL Shein invalide. Veuillez réessayer.</Message>
</Response>
```

### 4. 📈 Statistiques globales
```http
GET /stats
```

**Description**: Statistiques détaillées du système

**Réponse**:
```json
{
  "global_stats": {
    "total_orders": 156,
    "total_users": 23,
    "total_products": 89,
    "success_rate": 94.2,
    "avg_order_value": 25.67
  },
  "daily_stats": {
    "orders_today": 12,
    "new_users_today": 2,
    "revenue_today": 308.04
  },
  "top_users": [
    {
      "name": "Awa Diop",
      "phone": "whatsapp:+221701234567",
      "total_orders": 8,
      "total_spent": 156.78
    }
  ],
  "popular_products": [
    {
      "url": "https://www.shein.com/fr/item12345",
      "orders_count": 5,
      "total_quantity": 12
    }
  ]
}
```

### 5. 👤 Commandes utilisateur
```http
GET /user/{phone}/orders
```

**Description**: Récupérer les commandes d'un utilisateur spécifique

**Paramètres**:
- `phone`: Numéro WhatsApp (URL encodé, ex: `whatsapp%3A%2B221701234567`)

**Réponse**:
```json
{
  "user_info": {
    "phone": "whatsapp:+221701234567",
    "name": "Awa Diop",
    "total_orders": 5,
    "total_spent": 127.45
  },
  "orders": [
    {
      "id": "ORD_20240115_001",
      "product_url": "https://www.shein.com/fr/item12345",
      "size": "M",
      "color": "Rouge",
      "quantity": 2,
      "estimated_price": 25.99,
      "status": "completed",
      "created_at": "2024-01-15T08:30:00Z",
      "added_to_cart_at": "2024-01-15T08:32:15Z"
    }
  ]
}
```

### 6. 📋 Récapitulatif admin
```http
GET /admin/recap
GET /admin/recap?format=excel
GET /admin/recap?format=pdf
```

**Description**: Générer et télécharger un récapitulatif complet

**Paramètres de requête**:
- `format`: Format de sortie (`json`, `excel`, `pdf`)
- `user`: Filtrer par utilisateur (optionnel)
- `date_from`: Date de début (format: `YYYY-MM-DD`)
- `date_to`: Date de fin (format: `YYYY-MM-DD`)

**Réponse JSON**:
```json
{
  "summary": {
    "total_orders": 45,
    "total_amount": 1156.78,
    "unique_users": 12,
    "unique_products": 28
  },
  "orders": [...],
  "users": [...],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

**Réponse Excel/PDF**: Fichier binaire avec headers appropriés

### 7. 🔄 Actions admin
```http
POST /admin/process-pending
```

**Description**: Traiter manuellement les commandes en attente

**Réponse**:
```json
{
  "message": "Processing started",
  "pending_orders": 3,
  "estimated_time": "2-3 minutes"
}
```

```http
POST /admin/generate-recap
```

**Description**: Générer un récapitulatif immédiat

**Body (JSON)**:
```json
{
  "format": "excel",
  "send_whatsapp": true,
  "include_stats": true
}
```

### 8. 🏥 Health Check
```http
GET /health
```

**Description**: Vérification rapide de l'état du service

**Réponse**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": 86400,
  "version": "1.0.0"
}
```

## 🔐 Authentification

### Webhook Twilio
Les webhooks Twilio incluent une signature pour vérifier l'authenticité:

**Header**: `X-Twilio-Signature`

**Validation** (automatique dans le code):
```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(auth_token)
is_valid = validator.validate(url, post_vars, signature)
```

### Admin Endpoints
Protégés par vérification du numéro admin:

```python
if user_phone != Config.ADMIN_WHATSAPP_NUMBER:
    return {"error": "Unauthorized"}, 403
```

## 📝 Codes d'erreur

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Requête invalide | Vérifier les paramètres |
| 401 | Non autorisé | Vérifier l'authentification |
| 403 | Accès interdit | Vérifier les permissions admin |
| 404 | Ressource non trouvée | Vérifier l'URL |
| 429 | Trop de requêtes | Attendre avant de réessayer |
| 500 | Erreur serveur | Consulter les logs |

## 🔄 Webhooks sortants

### Notifications admin
Le système peut envoyer des notifications à l'admin via WhatsApp:

**Événements**:
- Nouvelle commande reçue
- Erreur d'ajout au panier
- Limite utilisateur atteinte
- Récapitulatif quotidien
- Erreur système critique

**Format des messages**:
```
🚨 ALERTE SHEIN_SEN

Événement: Erreur ajout panier
Utilisateur: Awa Diop (+221701234567)
Produit: https://www.shein.com/fr/item12345
Erreur: Produit non disponible

Heure: 15/01/2024 10:30
```

## 📊 Monitoring et Métriques

### Métriques collectées
- Nombre de messages WhatsApp reçus
- Temps de traitement par message
- Taux de succès d'extraction IA
- Taux de succès d'ajout au panier
- Erreurs par composant
- Utilisation mémoire et CPU

### Logs structurés
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "component": "whatsapp_listener",
  "event": "message_received",
  "user_phone": "whatsapp:+221701234567",
  "message_id": "SM1234567890abcdef",
  "processing_time": 1.23,
  "success": true
}
```

## 🧪 Tests d'API

### Avec curl
```bash
# Test de statut
curl -X GET http://localhost:5000/status

# Test webhook (simulation)
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp%3A%2B221701234567&To=whatsapp%3A%2B14155238886&Body=https%3A//www.shein.com/fr/item12345"

# Test récapitulatif
curl -X GET "http://localhost:5000/admin/recap?format=json"
```

### Avec Python
```python
import requests

# Test de statut
response = requests.get('http://localhost:5000/status')
print(response.json())

# Test webhook
data = {
    'From': 'whatsapp:+221701234567',
    'To': 'whatsapp:+14155238886',
    'Body': 'https://www.shein.com/fr/item12345 - Taille M'
}
response = requests.post('http://localhost:5000/webhook', data=data)
print(response.text)
```

## 🚀 Déploiement en production

### Variables d'environnement supplémentaires
```env
# Production
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000
HOST=0.0.0.0

# HTTPS
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Base URL publique
BASE_URL=https://votre-domaine.com

# Sécurité
SECRET_KEY=votre-cle-secrete-longue-et-complexe
TWILIO_WEBHOOK_SECRET=votre-secret-webhook-twilio
```

### Configuration nginx
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring avec systemd
```ini
[Unit]
Description=SHEIN_SEN Service
After=network.target

[Service]
Type=simple
User=sheinsen
WorkingDirectory=/opt/shein_sen
ExecStart=/opt/shein_sen/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

**📚 Cette documentation couvre tous les aspects de l'API SHEIN_SEN pour l'intégration et le monitoring.**