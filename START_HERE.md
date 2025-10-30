# 🎯 COMMENCEZ ICI

Bienvenue dans **oldsite-scanner** - Détecteur de vieux sites suisses .ch!

## ⚡ Démarrage ultra-rapide (2 minutes)

```bash
# 1. Ouvrir un terminal dans ce dossier
cd oldsite-scanner

# 2. Lancer le script de test
./test_local.sh

# 3. Choisir l'option 4 (tout tester)

# 4. Ouvrir votre navigateur sur http://127.0.0.1:8000
```

C'est tout! Vous verrez l'interface web avec les résultats du scan.

## 📚 Documentation

Le projet contient plusieurs guides selon votre besoin:

### 🚀 Pour commencer rapidement
- **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage rapide (5 min)
- **[START_HERE.md](START_HERE.md)** - Ce fichier

### 📖 Pour comprendre le projet
- **[README.md](README.md)** - Documentation complète du projet
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Résumé technique complet

### 🔧 Pour utiliser l'API
- **[API.md](API.md)** - Documentation complète de l'API REST

### 🚀 Pour déployer en production
- **[deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md)** - Guide de déploiement détaillé
- **[deployment/README.md](deployment/README.md)** - Fichiers de déploiement

### 🤝 Pour contribuer
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guide de contribution
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions

## 🎯 Que fait ce projet?

**oldsite-scanner** scanne automatiquement des sites web suisses (.ch) pour détecter:

- ❌ Sites sans HTTPS
- 🕰️ Serveurs web anciens (Apache 1.x, IIS 5/6)
- 🐘 PHP ancien (4.x, 5.x)
- 📄 HTML4 / XHTML 1.0
- 🔤 Encodage ISO-8859
- 🏷️ Balises obsolètes (`<font>`, `<center>`, etc.)
- 🔒 Headers de sécurité manquants
- 📱 Pas de support mobile

Chaque site reçoit un **score d'obsolescence** (0-200+). Plus le score est élevé, plus le site est ancien.

## 🏗️ Architecture

```
┌─────────────────┐
│  Scanner Python │  ← Scan asynchrone de domaines .ch
│   (asyncio)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Base SQLite    │  ← Stockage des résultats
│   (oldsites.db) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API FastAPI    │  ← Endpoints REST
│  (port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Interface Web  │  ← Consultation des résultats
│  (HTML/CSS/JS)  │
└─────────────────┘
```

## 📋 Checklist de démarrage

### Test local (recommandé)
- [ ] Cloner le projet
- [ ] Exécuter `./test_local.sh`
- [ ] Choisir option 4
- [ ] Ouvrir http://127.0.0.1:8000
- [ ] Explorer l'interface

### Installation manuelle
- [ ] Créer l'environnement virtuel: `python3 -m venv venv`
- [ ] Activer: `source venv/bin/activate`
- [ ] Installer: `pip install -r backend/requirements.txt`
- [ ] Générer domaines: `python -m backend.scan_ch_sites --generate-sample`
- [ ] Scanner: `python -m backend.scan_ch_sites --limit 10`
- [ ] Lancer API: `python -m backend.api`

### Déploiement serveur
- [ ] Avoir un serveur Ubuntu 22.04
- [ ] Avoir un nom de domaine
- [ ] Exécuter `./deployment/install.sh`
- [ ] Suivre les instructions

## 🎓 Exemples d'utilisation

### Scanner des domaines

```bash
# Générer un fichier d'exemple
python -m backend.scan_ch_sites --generate-sample

# Scanner 10 domaines
python -m backend.scan_ch_sites --limit 10

# Scanner avec un fichier personnalisé
python -m backend.scan_ch_sites --domains-file mes_domaines.txt
```

### Consulter les résultats

```bash
# Via l'interface web
open http://127.0.0.1:8000

# Via l'API
curl http://127.0.0.1:8000/api/scans?limit=10
curl http://127.0.0.1:8000/api/stats
```

### Personnaliser la configuration

Éditer `backend/config.py`:

```python
CONCURRENCY = 50          # Plus rapide
SCORE_THRESHOLD = 30      # Plus de résultats
HEAD_TIMEOUT = 5          # Plus patient
```

## 🔍 Comprendre les scores

| Score | Niveau | Description |
|-------|--------|-------------|
| 0-39 | ✅ Moderne | Site à jour (non enregistré) |
| 40-59 | ⚠️ Léger | Quelques éléments anciens |
| 60-79 | 🟠 Moyen | Plusieurs éléments anciens |
| 80-99 | 🔴 Élevé | Très obsolète |
| 100+ | 💀 Critique | Extrêmement ancien |

## 🛠️ Commandes utiles

```bash
# Vérifier le projet
./check_project.sh

# Tester localement
./test_local.sh

# Lancer l'API rapidement
./run_local.sh

# Scanner 5 domaines
python -m backend.scan_ch_sites --limit 5

# Voir l'aide
python -m backend.scan_ch_sites --help
```

## 🐛 Problèmes courants

### "Module not found"
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

### "Port 8000 already in use"
```bash
lsof -i :8000  # Trouver le processus
kill -9 <PID>  # Le tuer
```

### "No such file or directory: domains_ch.txt"
```bash
python -m backend.scan_ch_sites --generate-sample
```

### Aucun résultat après scan
```bash
# Diminuer le seuil dans backend/config.py
SCORE_THRESHOLD = 20  # Au lieu de 40
```

## 📊 Que faire ensuite?

1. **Tester localement** avec `./test_local.sh`
2. **Lire** [QUICKSTART.md](QUICKSTART.md) pour plus de détails
3. **Personnaliser** la liste de domaines dans `domains_ch.txt`
4. **Ajuster** les paramètres dans `backend/config.py`
5. **Déployer** sur un serveur avec `deployment/install.sh`
6. **Contribuer** en ajoutant de nouveaux critères

## 🎉 Fonctionnalités principales

✅ **Scanner asynchrone** - Rapide et efficace
✅ **20+ critères** de détection
✅ **Base SQLite** - Léger, pas de serveur
✅ **API REST** - Intégration facile
✅ **Interface moderne** - Responsive et intuitive
✅ **Déploiement simple** - Script automatique
✅ **Documentation complète** - 7 guides
✅ **Open source** - Licence MIT

## 💡 Cas d'usage

- 🔍 **Audit de sécurité** - Identifier les sites vulnérables
- 📊 **Étude statistique** - Analyser l'état du web suisse
- 🎓 **Recherche** - Étudier l'évolution des technologies
- 🏢 **Entreprise** - Surveiller son parc de sites
- 🎯 **Marketing** - Identifier des prospects

## 📞 Besoin d'aide?

1. **Documentation** - Lire les fichiers .md
2. **Issues GitHub** - Ouvrir une issue
3. **Email** - contact@votredomaine.ch

## 🚀 Prêt à commencer?

```bash
./test_local.sh
```

**Bon scan!** 🔍✨

---

*Créé avec ❤️ pour détecter les vieux sites suisses*
