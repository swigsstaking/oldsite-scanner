#!/bin/bash
# Script d'installation automatique pour oldsite-scanner sur Ubuntu 22.04

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que le script est exécuté sur Ubuntu
if [ ! -f /etc/os-release ]; then
    log_error "Impossible de détecter le système d'exploitation"
    exit 1
fi

. /etc/os-release
if [ "$ID" != "ubuntu" ]; then
    log_error "Ce script est conçu pour Ubuntu uniquement"
    exit 1
fi

log_info "Détection: $PRETTY_NAME"

# Vérifier les privilèges sudo
if [ "$EUID" -eq 0 ]; then 
    log_error "Ne pas exécuter ce script en tant que root. Utilisez sudo quand nécessaire."
    exit 1
fi

if ! sudo -v; then
    log_error "Ce script nécessite des privilèges sudo"
    exit 1
fi

log_info "Début de l'installation de oldsite-scanner"
echo ""

# Variables
INSTALL_DIR="/opt/oldsite-scanner"
REPO_URL="https://github.com/VOTRECOMPTE/oldsite-scanner.git"
DOMAIN=""

# Demander le nom de domaine
read -p "Entrez votre nom de domaine (ex: scanner.votredomaine.ch): " DOMAIN
if [ -z "$DOMAIN" ]; then
    log_error "Le nom de domaine est requis"
    exit 1
fi

log_info "Installation pour le domaine: $DOMAIN"
echo ""

# 1. Mise à jour du système
log_info "Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

# 2. Installation des dépendances
log_info "Installation des dépendances..."
sudo apt install -y python3 python3-venv python3-pip nginx git sqlite3

# 3. Création du répertoire
log_info "Création du répertoire $INSTALL_DIR..."
sudo mkdir -p $INSTALL_DIR
sudo chown -R $USER:$USER $INSTALL_DIR

# 4. Clonage du projet
log_info "Clonage du projet..."
if [ -d "$INSTALL_DIR/.git" ]; then
    log_warn "Le projet existe déjà, mise à jour..."
    cd $INSTALL_DIR
    git pull
else
    git clone $REPO_URL $INSTALL_DIR
    cd $INSTALL_DIR
fi

# 5. Configuration de l'environnement Python
log_info "Configuration de l'environnement virtuel Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 6. Génération d'un fichier de domaines d'exemple
log_info "Génération d'un fichier de domaines d'exemple..."
python -m backend.scan_ch_sites --generate-sample

# 7. Test de l'installation
log_info "Initialisation de la base de données..."
python -m backend.api &
API_PID=$!
sleep 3
kill $API_PID 2>/dev/null || true

# 8. Configuration du service systemd pour l'API
log_info "Configuration du service systemd pour l'API..."
sudo cp deployment/oldsites-api.service /etc/systemd/system/
sudo chown -R www-data:www-data $INSTALL_DIR
sudo systemctl daemon-reload
sudo systemctl enable oldsites-api
sudo systemctl start oldsites-api

# Vérifier que le service est démarré
sleep 2
if sudo systemctl is-active --quiet oldsites-api; then
    log_info "Service API démarré avec succès"
else
    log_error "Échec du démarrage du service API"
    sudo journalctl -u oldsites-api -n 20
    exit 1
fi

# 9. Configuration du scan automatique
log_info "Configuration du scan automatique..."
sudo cp deployment/oldsites-scan.service /etc/systemd/system/
sudo cp deployment/oldsites-scan.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable oldsites-scan.timer
sudo systemctl start oldsites-scan.timer

# 10. Configuration de Nginx
log_info "Configuration de Nginx..."
sudo cp deployment/nginx-site.conf /etc/nginx/sites-available/oldsites

# Remplacer le domaine dans la configuration
sudo sed -i "s/scanner.votredomaine.ch/$DOMAIN/g" /etc/nginx/sites-available/oldsites

# Activer le site
sudo ln -sf /etc/nginx/sites-available/oldsites /etc/nginx/sites-enabled/

# Tester la configuration
if sudo nginx -t; then
    log_info "Configuration Nginx valide"
    sudo systemctl reload nginx
else
    log_error "Configuration Nginx invalide"
    exit 1
fi

# 11. Configuration du firewall
log_info "Configuration du firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    log_info "Firewall configuré (ports 80 et 443 ouverts)"
else
    log_warn "UFW non installé, configuration du firewall ignorée"
fi

# 12. Installation de Certbot (optionnel)
read -p "Voulez-vous installer HTTPS avec Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Installation de Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
    
    log_info "Obtention du certificat SSL..."
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email || {
        log_warn "Échec de l'obtention du certificat SSL automatique"
        log_info "Vous pouvez le faire manuellement avec: sudo certbot --nginx -d $DOMAIN"
    }
fi

# 13. Protection par mot de passe (optionnel)
read -p "Voulez-vous protéger l'accès par mot de passe? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Configuration de la protection par mot de passe..."
    sudo apt install -y apache2-utils
    
    read -p "Nom d'utilisateur: " USERNAME
    sudo htpasswd -c /etc/nginx/.htpasswd $USERNAME
    
    # Activer l'authentification dans Nginx
    sudo sed -i 's/# auth_basic/auth_basic/g' /etc/nginx/sites-available/oldsites
    sudo systemctl reload nginx
    
    log_info "Protection par mot de passe activée"
fi

echo ""
log_info "═══════════════════════════════════════════════════════════"
log_info "Installation terminée avec succès!"
log_info "═══════════════════════════════════════════════════════════"
echo ""
log_info "📊 Informations:"
log_info "  - Répertoire: $INSTALL_DIR"
log_info "  - Domaine: $DOMAIN"
log_info "  - Base de données: $INSTALL_DIR/oldsites.db"
echo ""
log_info "🔧 Commandes utiles:"
log_info "  - Statut API: sudo systemctl status oldsites-api"
log_info "  - Logs API: sudo journalctl -u oldsites-api -f"
log_info "  - Statut scan: sudo systemctl status oldsites-scan.timer"
log_info "  - Lancer un scan: sudo systemctl start oldsites-scan.service"
log_info "  - Logs scan: sudo journalctl -u oldsites-scan -f"
echo ""
log_info "🌐 Accès:"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "  - Interface web: https://$DOMAIN"
    log_info "  - API: https://$DOMAIN/api/scans"
else
    log_info "  - Interface web: http://$DOMAIN"
    log_info "  - API: http://$DOMAIN/api/scans"
fi
echo ""
log_info "📝 Prochaines étapes:"
log_info "  1. Ajouter vos domaines dans: $INSTALL_DIR/domains_ch.txt"
log_info "  2. Lancer un premier scan: sudo systemctl start oldsites-scan.service"
log_info "  3. Consulter les résultats sur: http://$DOMAIN"
echo ""
log_info "Pour plus d'informations, consulter: $INSTALL_DIR/deployment/DEPLOYMENT.md"
echo ""
