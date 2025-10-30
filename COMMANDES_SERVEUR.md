# 📋 Commandes pour votre serveur

## 🚀 Installation (à faire une seule fois)

```bash
# 1. Cloner le projet
cd /opt
sudo mkdir -p oldsite-scanner
sudo chown -R $USER:$USER oldsite-scanner
cd oldsite-scanner
git clone https://github.com/swigsstaking/oldsite-scanner.git .

# 2. Installer
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Tester
python -m backend.scan_ch_sites --generate-sample
python -m backend.scan_ch_sites --limit 5
python -m backend.api
```

Accès: `http://IP_SERVEUR:8000`

---

## ⚡ Utilisation quotidienne

### Scanner des domaines

```bash
cd /opt/oldsite-scanner
source venv/bin/activate

# Scanner 10 domaines
python -m backend.scan_ch_sites --limit 10

# Scanner 100 domaines
python -m backend.scan_ch_sites --limit 100

# Scanner tous les domaines du fichier
python -m backend.scan_ch_sites
```

### Lancer l'API

```bash
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.api
```

Puis ouvrir: `http://IP_SERVEUR:8000`

### Consulter les résultats via API

```bash
# Statistiques
curl http://localhost:8000/api/stats

# Liste des scans
curl http://localhost:8000/api/scans?limit=20

# Détails d'un scan
curl http://localhost:8000/api/scans/1
```

---

## 🔄 Mise à jour

```bash
cd /opt/oldsite-scanner
git pull
source venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 🤖 Installation systemd (démarrage automatique)

```bash
# Installer les services
sudo cp deployment/oldsites-api.service /etc/systemd/system/
sudo cp deployment/oldsites-scan.service /etc/systemd/system/
sudo cp deployment/oldsites-scan.timer /etc/systemd/system/
sudo chown -R www-data:www-data /opt/oldsite-scanner
sudo systemctl daemon-reload
sudo systemctl enable --now oldsites-api
sudo systemctl enable --now oldsites-scan.timer
```

### Commandes systemd

```bash
# Voir le statut
sudo systemctl status oldsites-api

# Voir les logs
sudo journalctl -u oldsites-api -f

# Redémarrer
sudo systemctl restart oldsites-api

# Lancer un scan maintenant
sudo systemctl start oldsites-scan.service
```

---

## 📝 Personnaliser la liste de domaines

```bash
# Éditer le fichier
nano /opt/oldsite-scanner/domains_ch.txt

# Ajouter vos domaines (un par ligne)
admin.ch
sbb.ch
epfl.ch
```

---

## ⚙️ Configuration

Éditer `/opt/oldsite-scanner/backend/config.py`:

```python
CONCURRENCY = 50          # Nombre de requêtes simultanées
SCORE_THRESHOLD = 40      # Score minimum pour enregistrer
HEAD_TIMEOUT = 3          # Timeout en secondes
```

Puis redémarrer:
```bash
sudo systemctl restart oldsites-api
```

---

## 🔍 Accès à la base de données

```bash
# Ouvrir la base SQLite
sqlite3 /opt/oldsite-scanner/oldsites.db

# Voir les domaines
SELECT * FROM domains LIMIT 10;

# Voir les scans
SELECT * FROM scans ORDER BY score DESC LIMIT 10;

# Quitter
.quit
```

---

## 🆘 Dépannage rapide

### Port 8000 occupé
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Permissions
```bash
sudo chown -R www-data:www-data /opt/oldsite-scanner
```

### Réinitialiser la base
```bash
rm /opt/oldsite-scanner/oldsites.db
python -m backend.api  # Recrée la base
```

---

## 📊 URLs importantes

- Interface web: `http://IP_SERVEUR:8000`
- API Stats: `http://IP_SERVEUR:8000/api/stats`
- API Scans: `http://IP_SERVEUR:8000/api/scans`
- Documentation: `http://IP_SERVEUR:8000/docs`
