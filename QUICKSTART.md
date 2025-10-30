# ⚡ Guide de démarrage rapide

## 🚀 Démarrage en 5 minutes

### Option 1: Test local (recommandé pour débuter)

```bash
# 1. Cloner le projet
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git
cd oldsite-scanner

# 2. Lancer le script de test
chmod +x test_local.sh
./test_local.sh

# 3. Choisir l'option 4 (tout tester)
# L'interface sera accessible sur http://127.0.0.1:8000
```

### Option 2: Installation manuelle locale

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 2. Installer les dépendances
pip install -r backend/requirements.txt

# 3. Générer un fichier de domaines d'exemple
python -m backend.scan_ch_sites --generate-sample

# 4. Scanner quelques domaines
python -m backend.scan_ch_sites --limit 10

# 5. Lancer l'API
python -m backend.api

# 6. Ouvrir http://127.0.0.1:8000
```

### Option 3: Déploiement serveur (Ubuntu 22.04)

```bash
# 1. Connexion au serveur
ssh user@votre-serveur.ch

# 2. Cloner le projet
cd /tmp
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git
cd oldsite-scanner

# 3. Lancer l'installation automatique
chmod +x deployment/install.sh
./deployment/install.sh

# 4. Suivre les instructions à l'écran
```

## 📁 Structure du projet

```
oldsite-scanner/
├── backend/              # Code Python
│   ├── config.py        # Configuration
│   ├── db.py            # Base de données
│   ├── scan_ch_sites.py # Scanner
│   ├── api.py           # API FastAPI
│   └── requirements.txt # Dépendances
├── frontend/            # Interface web
│   └── index.html       # Page HTML
├── deployment/          # Fichiers de déploiement
│   ├── install.sh       # Script d'installation auto
│   ├── DEPLOYMENT.md    # Guide détaillé
│   ├── *.service        # Services systemd
│   └── nginx-site.conf  # Config Nginx
├── README.md            # Documentation principale
├── API.md               # Documentation API
├── CONTRIBUTING.md      # Guide de contribution
├── test_local.sh        # Script de test
└── run_local.sh         # Lancement rapide
```

## 🎯 Commandes essentielles

### Scanner des domaines

```bash
# Générer un fichier d'exemple
python -m backend.scan_ch_sites --generate-sample

# Scanner 10 domaines
python -m backend.scan_ch_sites --limit 10

# Scanner tous les domaines du fichier
python -m backend.scan_ch_sites

# Utiliser un fichier personnalisé
python -m backend.scan_ch_sites --domains-file mes_domaines.txt
```

### Lancer l'API

```bash
# Méthode 1: Script
./run_local.sh

# Méthode 2: Directement
python -m backend.api

# Méthode 3: Avec reload automatique
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

### Consulter les résultats

```bash
# Via l'interface web
open http://127.0.0.1:8000

# Via l'API
curl http://127.0.0.1:8000/api/scans?limit=10
curl http://127.0.0.1:8000/api/stats
```

## 🔧 Configuration rapide

Modifier `backend/config.py`:

```python
# Nombre de requêtes simultanées (augmenter pour aller plus vite)
CONCURRENCY = 30

# Score minimum pour enregistrer (diminuer pour plus de résultats)
SCORE_THRESHOLD = 40

# Timeouts en secondes
HEAD_TIMEOUT = 3
PARTIAL_GET_TIMEOUT = 5
```

## 📊 Comprendre les scores

| Score | Signification | Exemples |
|-------|---------------|----------|
| 0-39 | Site moderne | Non enregistré |
| 40-59 | Légèrement obsolète | Quelques critères anciens |
| 60-79 | Obsolète | Plusieurs critères anciens |
| 80-99 | Très obsolète | Nombreux critères anciens |
| 100+ | Extrêmement obsolète | Site très ancien |

### Critères principaux

- **+25 points**: Pas de HTTPS
- **+20 points**: PHP 4.x ou 5.0-5.2
- **+20 points**: DOCTYPE HTML 4
- **+15 points**: Apache/IIS ancien
- **+15 points**: Charset ISO-8859
- **+10 points**: Balises obsolètes (`<font>`, `<center>`, etc.)

## 🌐 Endpoints API

| Endpoint | Description |
|----------|-------------|
| `GET /` | Interface web |
| `GET /api/scans` | Liste des scans |
| `GET /api/scans/{id}` | Détails d'un scan |
| `GET /api/stats` | Statistiques |
| `GET /docs` | Documentation interactive |

## 🐛 Dépannage rapide

### Erreur: Module not found

```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate

# Réinstaller les dépendances
pip install -r backend/requirements.txt
```

### Erreur: Port 8000 déjà utilisé

```bash
# Trouver le processus
lsof -i :8000

# Tuer le processus
kill -9 <PID>

# Ou utiliser un autre port
uvicorn backend.api:app --port 8001
```

### Base de données corrompue

```bash
# Supprimer et recréer
rm oldsites.db
python -m backend.api  # Recrée automatiquement
```

### Aucun résultat après scan

```bash
# Vérifier le score threshold
# Diminuer dans config.py:
SCORE_THRESHOLD = 20  # Au lieu de 40

# Ou scanner plus de domaines
python -m backend.scan_ch_sites --limit 50
```

## 📚 Documentation complète

- **README.md**: Documentation principale et guide d'utilisation
- **API.md**: Documentation complète de l'API avec exemples
- **deployment/DEPLOYMENT.md**: Guide de déploiement détaillé
- **CONTRIBUTING.md**: Guide pour contribuer au projet

## 💡 Exemples d'utilisation

### Créer une liste de domaines personnalisée

```bash
# Créer le fichier
cat > mes_domaines.txt << EOF
admin.ch
sbb.ch
epfl.ch
ethz.ch
EOF

# Scanner
python -m backend.scan_ch_sites --domains-file mes_domaines.txt
```

### Exporter les résultats

```bash
# Via l'API (JSON)
curl http://127.0.0.1:8000/api/scans?limit=1000 > resultats.json

# Via SQLite (CSV)
sqlite3 oldsites.db << EOF
.headers on
.mode csv
.output resultats.csv
SELECT d.domain, s.score, s.reasons, s.scan_time 
FROM scans s JOIN domains d ON d.id=s.domain_id 
ORDER BY s.score DESC;
.quit
EOF
```

### Automatiser les scans (cron)

```bash
# Éditer le crontab
crontab -e

# Ajouter (scan quotidien à 3h)
0 3 * * * cd /chemin/vers/oldsite-scanner && /chemin/vers/venv/bin/python -m backend.scan_ch_sites --limit 500
```

## 🎓 Prochaines étapes

1. **Personnaliser** la liste de domaines dans `domains_ch.txt`
2. **Ajuster** les paramètres dans `backend/config.py`
3. **Déployer** sur un serveur avec `deployment/install.sh`
4. **Automatiser** les scans avec systemd timer ou cron
5. **Contribuer** en ajoutant de nouveaux critères de détection

## 🆘 Support

- **Documentation**: Lire README.md et API.md
- **Issues**: https://github.com/VOTRECOMPTE/oldsite-scanner/issues
- **Email**: contact@votredomaine.ch

---

**Bon scan!** 🔍
