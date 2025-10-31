# 🌐 Guide crt.sh - Récupération automatique des domaines .ch

## ✨ Nouvelles fonctionnalités

Votre scanner peut maintenant:
1. **Récupérer automatiquement** tous les domaines .ch depuis crt.sh (Certificate Transparency logs)
2. **Contrôler les jobs** depuis l'interface web (3 boutons)
3. **Voir le statut en temps réel** (idle / fetching / scanning)

## 🚀 Déploiement sur votre serveur

### 1. Mettre à jour le code

```bash
cd /opt/oldsite-scanner
git pull
```

### 2. Redémarrer l'API

```bash
# Si vous utilisez systemd
sudo systemctl restart oldsites-api

# Ou manuellement
cd /opt/oldsite-scanner
source venv/bin/activate
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### 3. Tester l'interface

Ouvrez votre navigateur sur `http://IP_SERVEUR:8000`

Vous verrez maintenant une nouvelle section **"⚙️ Contrôle des jobs"** avec 3 boutons.

## 🎮 Utilisation de l'interface

### Workflow complet

1. **Cliquez sur "1. 🌐 Récupérer les domaines (.ch)"**
   - Lance la récupération depuis crt.sh
   - Peut prendre 2-5 minutes
   - Le statut affiche "fetching"
   - Crée le fichier `domains_final.txt`

2. **Attendez que le statut passe à "idle"**
   - Le bouton "2. Scanner" devient actif
   - Le nombre de domaines s'affiche

3. **Cliquez sur "2. 🔍 Scanner"**
   - Lance le scan de 800 domaines (configurable)
   - Le statut affiche "scanning"
   - Les résultats apparaissent progressivement dans le tableau

4. **Si besoin, cliquez sur "⏹️ Arrêter"**
   - Arrête le job en cours
   - Retour à l'état "idle"

### États possibles

| État | Description | Boutons actifs |
|------|-------------|----------------|
| **idle** | Aucun job en cours | Récupérer, Scanner |
| **fetching** | Récupération des domaines | Arrêter |
| **scanning** | Scan en cours | Arrêter |

## 🧪 Test manuel (ligne de commande)

### Tester la récupération des domaines

```bash
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_crtsh
```

Vous verrez:
```
================================================================================
🌐 Récupération des domaines .ch depuis crt.sh
================================================================================

📅 Années interrogées: 2020 à 2025
📁 Fichier de sortie: /opt/oldsite-scanner/domains_final.txt

🔍 Interrogation crt.sh pour l'année 2020...
   ✅ 2020: 15234 domaines trouvés
🔍 Interrogation crt.sh pour l'année 2021...
   ✅ 2021: 18456 domaines trouvés
...
```

### Vérifier le fichier généré

```bash
# Voir le nombre de domaines
wc -l domains_final.txt

# Voir les premiers domaines
head -20 domains_final.txt

# Voir les derniers domaines
tail -20 domains_final.txt
```

### Scanner les domaines récupérés

```bash
# Scanner 100 domaines
python -m backend.scan_ch_sites --domains-file domains_final.txt --limit 100

# Scanner 500 domaines
python -m backend.scan_ch_sites --domains-file domains_final.txt --limit 500
```

## 📊 API Endpoints

### GET /api/job/status

Retourne l'état actuel:

```json
{
  "state": "idle",
  "pid": null,
  "started_at": null,
  "last_exit_code": 0,
  "last_job": "scan",
  "domains_file_exists": true,
  "domains_count": 45678
}
```

### POST /api/fetch/start

Lance la récupération des domaines:

```bash
curl -X POST http://localhost:8000/api/fetch/start
```

Réponse:
```json
{
  "status": "fetch_started",
  "pid": 12345,
  "started_at": "2025-10-31T15:30:00Z"
}
```

### POST /api/scan/start

Lance le scan:

```bash
curl -X POST http://localhost:8000/api/scan/start
```

Réponse:
```json
{
  "status": "scan_started",
  "pid": 12346,
  "started_at": "2025-10-31T15:35:00Z"
}
```

### POST /api/job/stop

Arrête le job en cours:

```bash
curl -X POST http://localhost:8000/api/job/stop
```

Réponse:
```json
{
  "status": "stopped",
  "pid": 12345,
  "job_type": "fetching",
  "message": "Job fetching arrêté"
}
```

## ⚙️ Configuration

### Modifier le nombre de domaines scannés

Éditez `backend/api.py`, ligne 182:

```python
cmd = f"{PYTHON_BIN} -m backend.scan_ch_sites --domains-file {DOMAINS_FILE} --limit 1500"
```

Puis redémarrez l'API.

### Modifier les années interrogées

Éditez `backend/fetch_crtsh.py`, ligne 15:

```python
YEARS = list(range(2018, 2026))  # 2018 à 2025
```

### Activer la vérification DNS

Éditez `backend/fetch_crtsh.py`, ligne 229:

```python
domains = await fetch_all_domains(verify_dns=True)  # Active la vérification
```

⚠️ **Attention**: La vérification DNS est très lente (peut prendre des heures pour 100k+ domaines)

## 🔍 Comment fonctionne crt.sh?

**crt.sh** est un moteur de recherche pour les Certificate Transparency logs. Il contient tous les certificats SSL/TLS émis publiquement.

### Avantages
- ✅ Gratuit et public
- ✅ Très complet (tous les domaines avec HTTPS)
- ✅ Mis à jour en temps réel
- ✅ Pas besoin d'authentification

### Limitations
- ⚠️ Seulement les domaines avec certificats SSL
- ⚠️ Peut contenir des sous-domaines
- ⚠️ Peut contenir des domaines expirés
- ⚠️ Rate limiting possible si trop de requêtes

### Stratégie de récupération

Le script interroge crt.sh par **année** pour éviter les timeouts:
- 2020: tous les certificats émis en 2020
- 2021: tous les certificats émis en 2021
- etc.

Puis il nettoie et déduplique les résultats.

## 📈 Performances

### Récupération des domaines
- **Durée**: 2-5 minutes (dépend de crt.sh)
- **Domaines trouvés**: 50'000 - 150'000 (selon les années)
- **Fichier généré**: 2-5 MB

### Scan des domaines
- **Vitesse**: ~100 domaines/minute (concurrence 30)
- **800 domaines**: ~8 minutes
- **5000 domaines**: ~50 minutes

## 🐛 Dépannage

### crt.sh ne répond pas

```bash
# Tester manuellement
curl "https://crt.sh/?q=%.ch&output=json&minNotBefore=2024-01-01&maxNotBefore=2024-12-31" | head
```

Si timeout, réessayez plus tard (crt.sh peut être surchargé).

### Aucun domaine trouvé

Vérifiez les logs:
```bash
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_crtsh
```

### Le bouton "Scanner" est désactivé

Le fichier `domains_final.txt` n'existe pas. Lancez d'abord la récupération.

### Le job ne s'arrête pas

```bash
# Trouver le PID
ps aux | grep fetch_crtsh
ps aux | grep scan_ch_sites

# Tuer manuellement
kill -9 <PID>
```

## 💡 Conseils

### Pour un scan complet

1. Récupérez les domaines (50k-150k domaines)
2. Scannez par lots:
   - Jour 1: 1000 domaines
   - Jour 2: 1000 domaines
   - etc.

Ou modifiez la limite dans l'API pour scanner plus:
```python
--limit 5000  # Au lieu de 800
```

### Pour cibler des domaines spécifiques

Après la récupération, filtrez `domains_final.txt`:

```bash
# Garder seulement les domaines courts (potentiellement plus vieux)
grep -E '^[a-z]{3,8}\.ch$' domains_final.txt > domains_short.txt

# Scanner ce fichier
python -m backend.scan_ch_sites --domains-file domains_short.txt --limit 500
```

### Pour automatiser

Créez un cron job:

```bash
crontab -e
```

Ajoutez:
```
# Récupérer les domaines tous les lundis à 2h
0 2 * * 1 cd /opt/oldsite-scanner && /opt/oldsite-scanner/venv/bin/python -m backend.fetch_crtsh

# Scanner 1000 domaines tous les jours à 3h
0 3 * * * cd /opt/oldsite-scanner && /opt/oldsite-scanner/venv/bin/python -m backend.scan_ch_sites --domains-file domains_final.txt --limit 1000
```

## 🎉 Résumé

Vous avez maintenant un système complet pour:
1. ✅ Récupérer automatiquement les domaines .ch depuis crt.sh
2. ✅ Contrôler les jobs depuis l'interface web
3. ✅ Scanner les domaines et détecter les vieux sites
4. ✅ Voir les résultats en temps réel

**Profitez-en!** 🚀
