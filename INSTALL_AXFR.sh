#!/bin/bash
# Script d'installation rapide du système AXFR

set -e

echo "🌐 Installation du système AXFR pour oldsite-scanner"
echo "===================================================="
echo ""

# 1. Installer dnsutils
echo "📦 Installation de dnsutils (dig)..."
sudo apt update
sudo apt install -y dnsutils

# 2. Tester dig
echo ""
echo "✅ dig installé: $(dig -v | head -1)"
echo ""

# 3. Copier les nouveaux services systemd
echo "📋 Installation des services systemd..."
sudo cp deployment/oldsites-fetch-domains.service /etc/systemd/system/
sudo cp deployment/oldsites-full-scan.service /etc/systemd/system/
sudo cp deployment/oldsites-full-scan.timer /etc/systemd/system/

# 4. Recharger systemd
sudo systemctl daemon-reload

# 5. Tester la récupération des domaines
echo ""
echo "🧪 Test de récupération des domaines .ch..."
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_ch_domains

# 6. Vérifier le fichier
if [ -f "domains_ch.txt" ]; then
    DOMAIN_COUNT=$(grep -v '^#' domains_ch.txt | grep -v '^$' | wc -l)
    echo ""
    echo "✅ Fichier domains_ch.txt créé avec $DOMAIN_COUNT domaines"
else
    echo ""
    echo "⚠️  Fichier domains_ch.txt non créé (AXFR a peut-être échoué)"
    echo "   Vous pouvez créer le fichier manuellement"
fi

# 7. Activer le timer
echo ""
echo "⏰ Activation du timer (scan quotidien à 3h00)..."
sudo systemctl enable oldsites-full-scan.timer
sudo systemctl start oldsites-full-scan.timer

# 8. Afficher le statut
echo ""
echo "📊 Statut du timer:"
sudo systemctl status oldsites-full-scan.timer --no-pager

echo ""
echo "🎯 Prochaine exécution:"
sudo systemctl list-timers | grep oldsites

echo ""
echo "=" * 80
echo "✅ Installation terminée!"
echo "=" * 80
echo ""
echo "📝 Commandes utiles:"
echo ""
echo "  # Lancer un scan complet maintenant"
echo "  sudo systemctl start oldsites-full-scan.service"
echo ""
echo "  # Voir les logs en temps réel"
echo "  sudo journalctl -u oldsites-full-scan -f"
echo ""
echo "  # Récupérer seulement les domaines (sans scanner)"
echo "  python -m backend.fetch_ch_domains"
echo ""
echo "  # Scanner 100 domaines"
echo "  python -m backend.scan_ch_sites --limit 100"
echo ""
echo "📖 Documentation complète: AXFR_SETUP.md"
echo ""
