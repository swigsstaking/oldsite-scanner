#!/bin/bash
# Script de test local pour oldsite-scanner

set -e

echo "🧪 Test local de oldsite-scanner"
echo "================================"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "backend/config.py" ]; then
    echo "❌ Erreur: Exécuter ce script depuis la racine du projet"
    exit 1
fi

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 détecté: $(python3 --version)"

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -q --upgrade pip
pip install -q -r backend/requirements.txt

echo "✓ Dépendances installées"
echo ""

# Générer un fichier de domaines d'exemple si nécessaire
if [ ! -f "domains_ch.txt" ]; then
    echo "📝 Génération d'un fichier de domaines d'exemple..."
    python -m backend.scan_ch_sites --generate-sample
    echo "✓ Fichier domains_ch.txt créé"
    echo ""
fi

# Menu de test
echo "Que voulez-vous tester?"
echo "1. Scanner 5 domaines"
echo "2. Scanner 10 domaines"
echo "3. Lancer l'API et l'interface web"
echo "4. Tout tester (scan + API)"
echo ""
read -p "Votre choix (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🔍 Scan de 5 domaines..."
        python -m backend.scan_ch_sites --limit 5
        ;;
    2)
        echo ""
        echo "🔍 Scan de 10 domaines..."
        python -m backend.scan_ch_sites --limit 10
        ;;
    3)
        echo ""
        echo "🚀 Lancement de l'API..."
        echo "   Interface web: http://127.0.0.1:8000"
        echo "   API: http://127.0.0.1:8000/api/scans"
        echo ""
        echo "   Appuyez sur Ctrl+C pour arrêter"
        echo ""
        python -m backend.api
        ;;
    4)
        echo ""
        echo "🔍 Scan de 10 domaines..."
        python -m backend.scan_ch_sites --limit 10
        echo ""
        echo "✓ Scan terminé"
        echo ""
        echo "🚀 Lancement de l'API..."
        echo "   Interface web: http://127.0.0.1:8000"
        echo "   API: http://127.0.0.1:8000/api/scans"
        echo ""
        echo "   Appuyez sur Ctrl+C pour arrêter"
        echo ""
        python -m backend.api
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac
