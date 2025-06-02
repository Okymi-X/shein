@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                        🛍️ SHEIN_SEN 🛍️                        ║
echo ║        Système d'Automatisation des Commandes Groupées       ║
echo ║                    Shein au Sénégal 🇸🇳                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Démarrage du système SHEIN_SEN...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 📥 Téléchargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo ⚠️ Fichier .env non trouvé
    echo 🔧 Exécutez d'abord: python setup.py
    pause
    exit /b 1
)

REM Vérifier si les dépendances sont installées
echo 📦 Vérification des dépendances...
python -c "import flask, openai, playwright" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Dépendances manquantes
    echo 📥 Installation des dépendances...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Échec de l'installation des dépendances
        pause
        exit /b 1
    )
    echo ✅ Dépendances installées
)

REM Démarrer le système
echo 🚀 Démarrage de SHEIN_SEN...
echo.
echo 📱 WhatsApp Webhook: http://localhost:5000/webhook
echo 📊 Interface de statut: http://localhost:5000/status
echo 🛑 Appuyez sur Ctrl+C pour arrêter
echo.

python main.py

echo.
echo 🛑 SHEIN_SEN arrêté
pause