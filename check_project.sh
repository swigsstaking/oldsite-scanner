#!/bin/bash
# Script de vérification de l'intégrité du projet

echo "🔍 Vérification du projet oldsite-scanner"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Fonction pour vérifier un fichier
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 MANQUANT"
        ((ERRORS++))
    fi
}

# Fonction pour vérifier un dossier
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/"
    else
        echo "❌ $1/ MANQUANT"
        ((ERRORS++))
    fi
}

# Fonction pour vérifier qu'un fichier est exécutable
check_executable() {
    if [ -x "$1" ]; then
        echo "✅ $1 (exécutable)"
    else
        echo "⚠️  $1 (pas exécutable)"
        ((WARNINGS++))
    fi
}

echo "📁 Structure des dossiers:"
check_dir "backend"
check_dir "frontend"
check_dir "deployment"
echo ""

echo "🐍 Fichiers backend:"
check_file "backend/__init__.py"
check_file "backend/config.py"
check_file "backend/db.py"
check_file "backend/scan_ch_sites.py"
check_file "backend/api.py"
check_file "backend/requirements.txt"
echo ""

echo "🌐 Fichiers frontend:"
check_file "frontend/index.html"
echo ""

echo "🚀 Fichiers de déploiement:"
check_file "deployment/install.sh"
check_file "deployment/oldsites-api.service"
check_file "deployment/oldsites-scan.service"
check_file "deployment/oldsites-scan.timer"
check_file "deployment/nginx-site.conf"
check_file "deployment/DEPLOYMENT.md"
check_file "deployment/README.md"
echo ""

echo "📚 Documentation:"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "API.md"
check_file "CONTRIBUTING.md"
check_file "CHANGELOG.md"
check_file "LICENSE"
check_file "PROJECT_SUMMARY.md"
echo ""

echo "🔧 Scripts:"
check_executable "run_local.sh"
check_executable "test_local.sh"
check_executable "deployment/install.sh"
echo ""

echo "📄 Autres fichiers:"
check_file ".gitignore"
check_file "domains_ch.example.txt"
echo ""

# Vérifier la syntaxe Python
echo "🐍 Vérification de la syntaxe Python:"
if command -v python3 &> /dev/null; then
    for file in backend/*.py; do
        if [ -f "$file" ]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                echo "✅ $file (syntaxe valide)"
            else
                echo "❌ $file (erreur de syntaxe)"
                ((ERRORS++))
            fi
        fi
    done
else
    echo "⚠️  Python 3 non installé, impossible de vérifier la syntaxe"
    ((WARNINGS++))
fi
echo ""

# Vérifier les dépendances
echo "📦 Vérification des dépendances:"
if [ -f "backend/requirements.txt" ]; then
    echo "✅ requirements.txt présent"
    echo "   Dépendances listées:"
    cat backend/requirements.txt | grep -v '^#' | grep -v '^$' | sed 's/^/     - /'
else
    echo "❌ requirements.txt manquant"
    ((ERRORS++))
fi
echo ""

# Résumé
echo "=========================================="
echo "📊 Résumé de la vérification:"
echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Projet complet et valide!"
    echo "   Aucune erreur détectée."
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "   1. ./test_local.sh pour tester localement"
    echo "   2. Lire QUICKSTART.md pour démarrer"
    echo "   3. ./deployment/install.sh pour déployer"
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Projet valide avec $WARNINGS avertissement(s)"
    echo "   Certains fichiers ne sont pas exécutables."
    echo "   Exécutez: chmod +x *.sh deployment/*.sh"
else
    echo "❌ $ERRORS erreur(s) et $WARNINGS avertissement(s) détecté(s)"
    echo "   Certains fichiers sont manquants."
fi
echo ""
