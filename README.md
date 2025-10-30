# 🕰️ Old .ch Scanner

Détecteur automatique de sites suisses obsolètes. Ce projet scanne les domaines `.ch` pour identifier les sites utilisant des technologies anciennes (PHP5, HTML4, ISO-8859, pas de HTTPS, etc.).

## 📋 Fonctionnalités

- ✅ Scan asynchrone de domaines .ch avec concurrence configurable
- ✅ Détection multi-critères (serveur, PHP, charset, DOCTYPE, balises obsolètes, etc.)
- ✅ Système de scoring pour évaluer le niveau d'obsolescence
- ✅ Base de données SQLite pour stocker les résultats
- ✅ API REST FastAPI pour consulter les résultats
- ✅ Interface web moderne et responsive
- ✅ Déployable sur Ubuntu 22.04 avec systemd et Nginx

## 🧱 Structure du projet

```
oldsite-scanner/
├── backend/
│   ├── __init__.py
│   ├── config.py          # Configuration du scanner
│   ├── db.py              # Gestion de la base de données
│   ├── scan_ch_sites.py   # Scanner asynchrone
│   ├── api.py             # API FastAPI
│   └── requirements.txt   # Dépendances Python
├── frontend/
│   └── index.html         # Interface web
├── run_local.sh           # Script de lancement local
├── .gitignore
└── README.md
```

## 🚀 Installation locale

### Prérequis

- Python 3.8+
- pip

### Installation

```bash
# Cloner le projet
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git
cd oldsite-scanner

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r backend/requirements.txt
```

### Utilisation

#### 1. Générer un fichier d'exemple de domaines

```bash
python -m backend.scan_ch_sites --generate-sample
```

Cela crée `domains_ch.txt` avec quelques domaines suisses populaires.

#### 2. Lancer un scan

```bash
# Scanner tous les domaines du fichier
python -m backend.scan_ch_sites

# Scanner seulement les 50 premiers domaines
python -m backend.scan_ch_sites --limit 50

# Utiliser un fichier de domaines personnalisé
python -m backend.scan_ch_sites --domains-file mes_domaines.txt
```

#### 3. Lancer l'API et l'interface web

```bash
# Méthode 1: Script de lancement
chmod +x run_local.sh
./run_local.sh

# Méthode 2: Commande directe
python -m backend.api
```

Ouvrir ensuite http://127.0.0.1:8000 dans votre navigateur.

## 🔧 Configuration

Modifier `backend/config.py` pour ajuster les paramètres:

```python
DB_FILE = "oldsites.db"              # Fichier de base de données
CONCURRENCY = 30                      # Nombre de requêtes simultanées
HEAD_TIMEOUT = 3                      # Timeout pour HEAD request (secondes)
PARTIAL_GET_TIMEOUT = 5               # Timeout pour GET request (secondes)
USER_AGENT = "ChAuditBot/1.0 ..."    # User-Agent utilisé
SAMPLE_BYTES = 2048                   # Nombre d'octets HTML à analyser
SCORE_THRESHOLD = 40                  # Score minimum pour enregistrer
DOMAINS_FILE = "domains_ch.txt"       # Fichier de domaines par défaut
```

## 📊 Critères de détection

Le scanner attribue des points selon différents critères:

| Critère | Points | Description |
|---------|--------|-------------|
| Pas de HTTPS | 25 | Site accessible uniquement en HTTP |
| Apache 1.x/2.0/2.2 | 15 | Serveur web ancien |
| IIS 5/6/7 | 15 | Serveur Microsoft ancien |
| PHP 4.x/5.0-5.2 | 20 | Version PHP très ancienne |
| PHP 5.3-5.5 | 15 | Version PHP 5.x ancienne |
| Charset ISO-8859 | 15 | Encodage ancien |
| DOCTYPE HTML 4 | 20 | Standard HTML ancien |
| DOCTYPE XHTML 1.0 | 15 | Standard XHTML ancien |
| Balises obsolètes | 10 | `<font>`, `<center>`, `<marquee>`, etc. |
| Pas de meta viewport | 5 | Site non optimisé mobile |
| Headers de sécurité manquants | 10 | Absence de headers modernes |

**Score ≥ 40** : Site considéré comme ancien et enregistré dans la base.

## 🌐 API Endpoints

### `GET /api/scans`

Liste les scans avec filtres.

**Paramètres:**
- `min_score` (int, défaut: 0) - Score minimum
- `limit` (int, défaut: 200) - Nombre maximum de résultats

**Exemple:**
```bash
curl "http://127.0.0.1:8000/api/scans?min_score=60&limit=50"
```

### `GET /api/scans/{scan_id}`

Détails complets d'un scan (headers, HTML sample).

**Exemple:**
```bash
curl "http://127.0.0.1:8000/api/scans/1"
```

### `GET /api/stats`

Statistiques globales (nombre de scans, score moyen, etc.).

**Exemple:**
```bash
curl "http://127.0.0.1:8000/api/stats"
```

## 🖥️ Déploiement sur Ubuntu 22.04

### 1. Préparation du serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install -y python3-venv python3-pip nginx

# Création du répertoire
sudo mkdir -p /opt/oldsite-scanner
sudo chown -R $USER:$USER /opt/oldsite-scanner
cd /opt/oldsite-scanner

# Clonage du projet
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git .

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Service systemd pour l'API

Créer `/etc/systemd/system/oldsites-api.service`:

```ini
[Unit]
Description=Old .ch scanner API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/oldsite-scanner
Environment="PATH=/opt/oldsite-scanner/venv/bin"
ExecStart=/opt/oldsite-scanner/venv/bin/uvicorn backend.api:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer le service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oldsites-api
sudo systemctl start oldsites-api
sudo systemctl status oldsites-api
```

### 3. Scan automatique avec systemd timer

**Service:** `/etc/systemd/system/oldsites-scan.service`

```ini
[Unit]
Description=Old .ch scanner - batch scan

[Service]
Type=oneshot
WorkingDirectory=/opt/oldsite-scanner
Environment="PATH=/opt/oldsite-scanner/venv/bin"
ExecStart=/opt/oldsite-scanner/venv/bin/python -m backend.scan_ch_sites --limit 500
```

**Timer:** `/etc/systemd/system/oldsites-scan.timer`

```ini
[Unit]
Description=Run oldsites scan daily

[Timer]
OnCalendar=*-*-* 03:15:00
Persistent=true

[Install]
WantedBy=timers.target
```

Activer le timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now oldsites-scan.timer
sudo systemctl list-timers  # Vérifier
```

### 4. Configuration Nginx

Créer `/etc/nginx/sites-available/oldsites`:

```nginx
server {
    listen 80;
    server_name scanner.votredomaine.ch;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activer le site:

```bash
sudo ln -s /etc/nginx/sites-available/oldsites /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. HTTPS avec Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d scanner.votredomaine.ch
```

### 6. Firewall

```bash
sudo ufw allow 80,443/tcp
sudo ufw allow from VOTRE_IP to any port 22
sudo ufw enable
```

### 7. (Optionnel) Protection HTTP Basic Auth

```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

Ajouter dans le bloc `location /` de Nginx:

```nginx
auth_basic "Restricted Area";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Puis recharger Nginx:

```bash
sudo systemctl reload nginx
```

## 🔄 Mise à jour du projet

```bash
cd /opt/oldsite-scanner
git pull
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart oldsites-api
```

## 📝 Logs et monitoring

```bash
# Logs de l'API
sudo journalctl -u oldsites-api -f

# Logs du scan
sudo journalctl -u oldsites-scan -f

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🛠️ Développement

### Ajouter de nouveaux critères de détection

Modifier la fonction `score_site()` dans `backend/scan_ch_sites.py`:

```python
def score_site(headers, body_sample):
    score = 0
    reasons = []
    
    # Ajouter vos critères ici
    if 'mon-critere' in body_sample.lower():
        score += 10
        reasons.append("Mon critère détecté")
    
    return score, "; ".join(reasons)
```

### Ajouter de nouveaux endpoints API

Modifier `backend/api.py`:

```python
@app.get("/api/mon-endpoint")
async def mon_endpoint():
    return {"message": "Hello"}
```

## 📄 Licence

MIT

## 👤 Auteur

Votre nom - contact@votredomaine.ch

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.

## ⚠️ Avertissement

Ce scanner est conçu à des fins éducatives et d'audit. Assurez-vous d'avoir l'autorisation nécessaire avant de scanner des sites web. Utilisez un User-Agent identifiable et respectez les fichiers `robots.txt`.
