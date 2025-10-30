# 📦 Fichiers de déploiement

Ce dossier contient tous les fichiers nécessaires pour déployer oldsite-scanner sur un serveur Ubuntu 22.04.

## 📄 Fichiers

### Scripts

- **`install.sh`** - Script d'installation automatique
  - Installation complète en une commande
  - Configuration interactive
  - Vérifications et validation

### Configuration systemd

- **`oldsites-api.service`** - Service pour l'API FastAPI
  - Démarrage automatique au boot
  - Restart automatique en cas d'erreur
  - User: www-data

- **`oldsites-scan.service`** - Service pour le scan batch
  - Exécution oneshot
  - Scan de 500 domaines par défaut

- **`oldsites-scan.timer`** - Timer pour automatisation
  - Exécution quotidienne à 3h15
  - Persistent (rattrapage si serveur éteint)

### Configuration Nginx

- **`nginx-site.conf`** - Configuration du reverse proxy
  - Proxy vers FastAPI (port 8000)
  - Logs dédiés
  - Support HTTPS (via Certbot)
  - HTTP Basic Auth (commenté par défaut)

### Documentation

- **`DEPLOYMENT.md`** - Guide de déploiement complet
  - Instructions pas à pas
  - Configuration détaillée
  - Monitoring et maintenance
  - Dépannage

## 🚀 Utilisation rapide

### Installation automatique

```bash
# 1. Cloner le projet
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git
cd oldsite-scanner

# 2. Lancer l'installation
chmod +x deployment/install.sh
./deployment/install.sh

# 3. Suivre les instructions
```

### Installation manuelle

Suivre les instructions détaillées dans `DEPLOYMENT.md`.

## 📋 Checklist de déploiement

- [ ] Serveur Ubuntu 22.04 accessible
- [ ] Nom de domaine configuré (DNS)
- [ ] Ports 80 et 443 ouverts
- [ ] Accès sudo sur le serveur
- [ ] Git installé

## 🔧 Personnalisation

### Modifier le port de l'API

Dans `oldsites-api.service`:
```ini
ExecStart=/opt/oldsite-scanner/venv/bin/uvicorn backend.api:app --host 127.0.0.1 --port 8001
```

Dans `nginx-site.conf`:
```nginx
proxy_pass http://127.0.0.1:8001;
```

### Modifier la fréquence des scans

Dans `oldsites-scan.timer`:
```ini
# Toutes les 6 heures
OnCalendar=*-*-* 00,06,12,18:00:00

# Tous les lundis à 3h
OnCalendar=Mon *-*-* 03:00:00

# Tous les jours à 3h et 15h
OnCalendar=*-*-* 03,15:00:00
```

### Modifier le nombre de domaines scannés

Dans `oldsites-scan.service`:
```ini
ExecStart=/opt/oldsite-scanner/venv/bin/python -m backend.scan_ch_sites --limit 1000
```

## 🔍 Vérification post-installation

```bash
# Services
sudo systemctl status oldsites-api
sudo systemctl status oldsites-scan.timer

# Logs
sudo journalctl -u oldsites-api -f
sudo journalctl -u oldsites-scan -f

# Nginx
sudo nginx -t
sudo systemctl status nginx

# API
curl http://127.0.0.1:8000/api/stats
```

## 📊 Monitoring

### Logs systemd

```bash
# API
sudo journalctl -u oldsites-api -n 100
sudo journalctl -u oldsites-api --since "1 hour ago"

# Scan
sudo journalctl -u oldsites-scan -n 100
sudo journalctl -u oldsites-scan --since today
```

### Logs Nginx

```bash
sudo tail -f /var/log/nginx/oldsites_access.log
sudo tail -f /var/log/nginx/oldsites_error.log
```

### Espace disque

```bash
# Taille de la base de données
du -h /opt/oldsite-scanner/oldsites.db

# Espace disponible
df -h /opt/oldsite-scanner
```

## 🔄 Mise à jour

```bash
cd /opt/oldsite-scanner
git pull
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart oldsites-api
```

## 🆘 Dépannage

Consulter `DEPLOYMENT.md` section "Dépannage" pour:
- API ne démarre pas
- Nginx retourne 502
- Scan ne s'exécute pas
- Problèmes de permissions

## 📞 Support

- Documentation complète: `DEPLOYMENT.md`
- Issues GitHub: https://github.com/VOTRECOMPTE/oldsite-scanner/issues
- Email: contact@votredomaine.ch
