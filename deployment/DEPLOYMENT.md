# 🚀 Guide de déploiement sur Ubuntu 22.04

Ce guide détaille le déploiement complet du projet oldsite-scanner sur un serveur Ubuntu 22.04.

## 📋 Prérequis

- Serveur Ubuntu 22.04 LTS
- Accès root ou sudo
- Nom de domaine pointant vers le serveur (ex: scanner.votredomaine.ch)
- Port 80 et 443 ouverts

## 🔧 Installation pas à pas

### 1. Connexion au serveur

```bash
ssh user@votre-serveur.ch
```

### 2. Mise à jour du système

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Installation des dépendances

```bash
sudo apt install -y python3 python3-venv python3-pip nginx git
```

### 4. Création du répertoire du projet

```bash
sudo mkdir -p /opt/oldsite-scanner
sudo chown -R $USER:$USER /opt/oldsite-scanner
cd /opt/oldsite-scanner
```

### 5. Clonage du projet

```bash
# Remplacer par votre repository
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git .
```

### 6. Configuration de l'environnement Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 7. Test de l'installation

```bash
# Générer un fichier d'exemple de domaines
python -m backend.scan_ch_sites --generate-sample

# Lancer un scan test (limité à 10 domaines)
python -m backend.scan_ch_sites --limit 10

# Tester l'API
python -m backend.api
```

Ouvrir un autre terminal et tester:
```bash
curl http://127.0.0.1:8000/api/stats
```

Si tout fonctionne, arrêter l'API (Ctrl+C).

### 8. Configuration du service systemd pour l'API

```bash
# Copier le fichier de service
sudo cp deployment/oldsites-api.service /etc/systemd/system/

# Ajuster les permissions
sudo chown -R www-data:www-data /opt/oldsite-scanner

# Recharger systemd
sudo systemctl daemon-reload

# Activer et démarrer le service
sudo systemctl enable oldsites-api
sudo systemctl start oldsites-api

# Vérifier le statut
sudo systemctl status oldsites-api
```

### 9. Configuration du scan automatique

```bash
# Copier les fichiers de service et timer
sudo cp deployment/oldsites-scan.service /etc/systemd/system/
sudo cp deployment/oldsites-scan.timer /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le timer (scan quotidien à 3h15)
sudo systemctl enable oldsites-scan.timer
sudo systemctl start oldsites-scan.timer

# Vérifier que le timer est actif
sudo systemctl list-timers | grep oldsites

# Test manuel du scan
sudo systemctl start oldsites-scan.service
sudo journalctl -u oldsites-scan -f
```

### 10. Configuration de Nginx

```bash
# Copier la configuration
sudo cp deployment/nginx-site.conf /etc/nginx/sites-available/oldsites

# Modifier le nom de domaine
sudo nano /etc/nginx/sites-available/oldsites
# Remplacer "scanner.votredomaine.ch" par votre domaine

# Activer le site
sudo ln -s /etc/nginx/sites-available/oldsites /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### 11. Configuration du firewall

```bash
# Autoriser HTTP et HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Autoriser SSH depuis votre IP uniquement (recommandé)
sudo ufw allow from VOTRE_IP to any port 22

# Activer le firewall
sudo ufw enable

# Vérifier le statut
sudo ufw status
```

### 12. Installation de HTTPS avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d scanner.votredomaine.ch

# Tester le renouvellement automatique
sudo certbot renew --dry-run
```

### 13. (Optionnel) Protection par mot de passe

```bash
# Installer apache2-utils
sudo apt install -y apache2-utils

# Créer un utilisateur
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Modifier la configuration Nginx
sudo nano /etc/nginx/sites-available/oldsites

# Décommenter les lignes:
# auth_basic "Restricted Area";
# auth_basic_user_file /etc/nginx/.htpasswd;

# Recharger Nginx
sudo systemctl reload nginx
```

## 🔍 Vérification de l'installation

### Vérifier les services

```bash
# API
sudo systemctl status oldsites-api

# Timer de scan
sudo systemctl status oldsites-scan.timer

# Nginx
sudo systemctl status nginx
```

### Vérifier les logs

```bash
# Logs de l'API
sudo journalctl -u oldsites-api -f

# Logs du scan
sudo journalctl -u oldsites-scan -f

# Logs Nginx
sudo tail -f /var/log/nginx/oldsites_access.log
sudo tail -f /var/log/nginx/oldsites_error.log
```

### Tester l'API

```bash
# Stats
curl https://scanner.votredomaine.ch/api/stats

# Liste des scans
curl https://scanner.votredomaine.ch/api/scans?limit=10
```

### Tester l'interface web

Ouvrir dans un navigateur: https://scanner.votredomaine.ch

## 📊 Monitoring

### Vérifier l'espace disque

```bash
df -h
du -sh /opt/oldsite-scanner/oldsites.db
```

### Vérifier les processus

```bash
ps aux | grep uvicorn
```

### Vérifier les connexions

```bash
sudo netstat -tlnp | grep 8000
```

## 🔄 Maintenance

### Mise à jour du code

```bash
cd /opt/oldsite-scanner
git pull
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart oldsites-api
```

### Sauvegarder la base de données

```bash
# Créer un backup
sudo cp /opt/oldsite-scanner/oldsites.db /opt/oldsite-scanner/oldsites.db.backup

# Ou avec date
sudo cp /opt/oldsite-scanner/oldsites.db /opt/oldsite-scanner/oldsites.db.$(date +%Y%m%d)
```

### Nettoyer les vieux scans

```bash
# Se connecter à la base de données
sqlite3 /opt/oldsite-scanner/oldsites.db

# Supprimer les scans de plus de 90 jours
DELETE FROM scans WHERE scan_time < strftime('%s', 'now', '-90 days');

# Optimiser la base
VACUUM;

# Quitter
.quit
```

### Redémarrer les services

```bash
# Redémarrer l'API
sudo systemctl restart oldsites-api

# Forcer un scan maintenant
sudo systemctl start oldsites-scan.service
```

## 🐛 Dépannage

### L'API ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u oldsites-api -n 50

# Vérifier les permissions
ls -la /opt/oldsite-scanner

# Tester manuellement
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.api
```

### Nginx retourne 502 Bad Gateway

```bash
# Vérifier que l'API est en cours d'exécution
sudo systemctl status oldsites-api

# Vérifier que le port 8000 est ouvert
sudo netstat -tlnp | grep 8000

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/error.log
```

### Le scan ne s'exécute pas

```bash
# Vérifier le timer
sudo systemctl status oldsites-scan.timer

# Lancer manuellement
sudo systemctl start oldsites-scan.service

# Vérifier les logs
sudo journalctl -u oldsites-scan -f
```

### Problèmes de permissions

```bash
# Réinitialiser les permissions
sudo chown -R www-data:www-data /opt/oldsite-scanner
sudo chmod -R 755 /opt/oldsite-scanner
```

## 📈 Optimisation

### Augmenter la concurrence

Modifier `/opt/oldsite-scanner/backend/config.py`:

```python
CONCURRENCY = 50  # Au lieu de 30
```

Puis redémarrer:
```bash
sudo systemctl restart oldsites-api
```

### Ajuster les timeouts

Modifier les valeurs dans `config.py`:

```python
HEAD_TIMEOUT = 5
PARTIAL_GET_TIMEOUT = 8
```

### Planifier plusieurs scans par jour

Modifier `/etc/systemd/system/oldsites-scan.timer`:

```ini
[Timer]
OnCalendar=*-*-* 03:15:00
OnCalendar=*-*-* 15:15:00
```

Puis recharger:
```bash
sudo systemctl daemon-reload
sudo systemctl restart oldsites-scan.timer
```

## 🔒 Sécurité

### Limiter l'accès SSH

```bash
# Éditer la configuration SSH
sudo nano /etc/ssh/sshd_config

# Désactiver le login root
PermitRootLogin no

# Utiliser uniquement des clés SSH
PasswordAuthentication no

# Redémarrer SSH
sudo systemctl restart sshd
```

### Configurer fail2ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Mettre à jour régulièrement

```bash
# Créer un cron pour les mises à jour automatiques
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📞 Support

En cas de problème, vérifier:
1. Les logs systemd: `sudo journalctl -u oldsites-api -f`
2. Les logs Nginx: `sudo tail -f /var/log/nginx/error.log`
3. L'état des services: `sudo systemctl status oldsites-api`
4. Les permissions: `ls -la /opt/oldsite-scanner`

Pour plus d'informations, consulter le README.md principal.
