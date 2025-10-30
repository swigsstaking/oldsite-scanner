# 🚀 Déploiement en local sur votre serveur

## 📦 Installation rapide

### 1. Sur votre serveur, cloner le projet

```bash
# Installer Git si nécessaire
sudo apt update
sudo apt install -y git

# Cloner le projet (privé)
cd /opt
sudo mkdir -p oldsite-scanner
sudo chown -R $USER:$USER oldsite-scanner
cd oldsite-scanner
git clone https://github.com/swigsstaking/oldsite-scanner.git .
```

### 2. Installer les dépendances

```bash
# Installer Python et Nginx
sudo apt install -y python3 python3-venv python3-pip nginx

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
pip install -r backend/requirements.txt
```

### 3. Tester l'installation

```bash
# Générer un fichier de domaines d'exemple
python -m backend.scan_ch_sites --generate-sample

# Scanner 5 domaines pour tester
python -m backend.scan_ch_sites --limit 5

# Lancer l'API
python -m backend.api
```

L'API sera accessible sur `http://localhost:8000` ou `http://IP_SERVEUR:8000`

### 4. Configuration systemd (pour démarrage automatique)

```bash
# Copier les services
sudo cp deployment/oldsites-api.service /etc/systemd/system/
sudo cp deployment/oldsites-scan.service /etc/systemd/system/
sudo cp deployment/oldsites-scan.timer /etc/systemd/system/

# Ajuster les permissions
sudo chown -R www-data:www-data /opt/oldsite-scanner

# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable oldsites-api
sudo systemctl start oldsites-api
sudo systemctl enable oldsites-scan.timer
sudo systemctl start oldsites-scan.timer

# Vérifier
sudo systemctl status oldsites-api
```

### 5. Configuration Nginx (optionnel - pour accès via port 80)

```bash
# Copier la config
sudo cp deployment/nginx-site.conf /etc/nginx/sites-available/oldsites

# Éditer pour mettre localhost
sudo nano /etc/nginx/sites-available/oldsites
# Remplacer "scanner.votredomaine.ch" par "localhost" ou votre IP

# Activer
sudo ln -s /etc/nginx/sites-available/oldsites /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Accès à l'interface

### Accès direct (sans Nginx)
```
http://localhost:8000
http://IP_SERVEUR:8000
```

### Accès via Nginx (port 80)
```
http://localhost
http://IP_SERVEUR
```

## 📊 Commandes utiles

```bash
# Voir les logs de l'API
sudo journalctl -u oldsites-api -f

# Voir les logs du scan
sudo journalctl -u oldsites-scan -f

# Lancer un scan manuellement
sudo systemctl start oldsites-scan.service

# Redémarrer l'API
sudo systemctl restart oldsites-api

# Voir le statut
sudo systemctl status oldsites-api
sudo systemctl status oldsites-scan.timer
```

## 🔄 Mise à jour du projet

```bash
cd /opt/oldsite-scanner
git pull
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart oldsites-api
```

## 🛠️ Configuration personnalisée

Éditer `/opt/oldsite-scanner/backend/config.py`:

```python
# Augmenter la concurrence pour aller plus vite
CONCURRENCY = 50

# Diminuer le seuil pour avoir plus de résultats
SCORE_THRESHOLD = 30

# Ajuster les timeouts
HEAD_TIMEOUT = 5
PARTIAL_GET_TIMEOUT = 8
```

Puis redémarrer:
```bash
sudo systemctl restart oldsites-api
```

## 📝 Ajouter vos domaines

Créer ou éditer `/opt/oldsite-scanner/domains_ch.txt`:

```bash
nano /opt/oldsite-scanner/domains_ch.txt
```

Ajouter vos domaines (un par ligne):
```
admin.ch
sbb.ch
epfl.ch
# etc...
```

Puis lancer un scan:
```bash
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.scan_ch_sites --limit 100
```

## 🔒 Sécurité (accès local uniquement)

Si vous voulez que l'API soit accessible uniquement en local, modifier `/etc/systemd/system/oldsites-api.service`:

```ini
ExecStart=/opt/oldsite-scanner/venv/bin/uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Puis:
```bash
sudo systemctl daemon-reload
sudo systemctl restart oldsites-api
```

L'API ne sera accessible que depuis le serveur lui-même (pas depuis l'extérieur).

## 🆘 Dépannage

### L'API ne démarre pas
```bash
# Vérifier les logs
sudo journalctl -u oldsites-api -n 50

# Tester manuellement
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.api
```

### Port 8000 déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :8000

# Le tuer
sudo kill -9 <PID>

# Ou changer le port dans oldsites-api.service
```

### Permissions
```bash
sudo chown -R www-data:www-data /opt/oldsite-scanner
sudo chmod -R 755 /opt/oldsite-scanner
```

## ✅ Vérification finale

```bash
# Vérifier que tout fonctionne
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/scans?limit=5
```

Vous devriez voir du JSON en réponse.
