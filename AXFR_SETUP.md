# 🌐 Configuration AXFR - Récupération automatique des domaines .ch

Ce guide explique comment configurer la récupération automatique de tous les domaines .ch via transfert de zone AXFR.

## 📋 Prérequis

### Installer dnsutils (pour la commande dig)

```bash
sudo apt update
sudo apt install -y dnsutils
```

Vérifier l'installation:
```bash
dig -v
```

## 🧪 Test manuel

### 1. Tester la récupération des domaines

```bash
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_ch_domains
```

Cette commande va:
1. ✅ Tenter un AXFR sur `zonedata.switch.ch`
2. ✅ Si échec, essayer des serveurs alternatifs (ns1.nic.ch, ns2.nic.ch, etc.)
3. ✅ Créer/mettre à jour `domains_ch.txt` avec tous les domaines trouvés
4. ✅ Si tout échoue, conserver le fichier existant (pas d'erreur bloquante)

### 2. Vérifier le fichier généré

```bash
# Voir le nombre de domaines
wc -l domains_ch.txt

# Voir les premiers domaines
head -20 domains_ch.txt

# Voir les derniers domaines
tail -20 domains_ch.txt
```

### 3. Tester le scan complet

```bash
# Scanner 10 domaines pour tester
python -m backend.scan_ch_sites --limit 10

# Scanner 100 domaines
python -m backend.scan_ch_sites --limit 100
```

## 🤖 Automatisation avec systemd

### Installation

```bash
# Copier les nouveaux services
sudo cp deployment/oldsites-fetch-domains.service /etc/systemd/system/
sudo cp deployment/oldsites-full-scan.service /etc/systemd/system/
sudo cp deployment/oldsites-full-scan.timer /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le timer (scan quotidien à 3h00)
sudo systemctl enable oldsites-full-scan.timer
sudo systemctl start oldsites-full-scan.timer

# Vérifier que le timer est actif
sudo systemctl list-timers | grep oldsites
```

### Test manuel du pipeline complet

```bash
# Lancer manuellement le pipeline (fetch + scan)
sudo systemctl start oldsites-full-scan.service

# Voir les logs en temps réel
sudo journalctl -u oldsites-full-scan -f
```

## 📊 Services disponibles

### 1. `oldsites-fetch-domains.service`
Récupère uniquement les domaines via AXFR (sans scanner).

```bash
# Lancer
sudo systemctl start oldsites-fetch-domains.service

# Logs
sudo journalctl -u oldsites-fetch-domains -n 50
```

### 2. `oldsites-full-scan.service`
Pipeline complet: récupération des domaines + scan (1000 domaines par défaut).

```bash
# Lancer
sudo systemctl start oldsites-full-scan.service

# Logs
sudo journalctl -u oldsites-full-scan -f
```

### 3. `oldsites-full-scan.timer`
Timer pour exécuter automatiquement le pipeline tous les jours à 3h00.

```bash
# Statut
sudo systemctl status oldsites-full-scan.timer

# Voir quand sera la prochaine exécution
sudo systemctl list-timers | grep oldsites

# Désactiver
sudo systemctl stop oldsites-full-scan.timer
sudo systemctl disable oldsites-full-scan.timer
```

## ⚙️ Configuration

### Modifier le nombre de domaines scannés

Éditer `/etc/systemd/system/oldsites-full-scan.service`:

```ini
# Scanner 5000 domaines au lieu de 1000
ExecStart=/opt/oldsite-scanner/venv/bin/python -m backend.scan_ch_sites --limit 5000

# Scanner TOUS les domaines (attention: peut prendre des heures!)
ExecStart=/opt/oldsite-scanner/venv/bin/python -m backend.scan_ch_sites
```

Puis:
```bash
sudo systemctl daemon-reload
```

### Modifier la fréquence du scan

Éditer `/etc/systemd/system/oldsites-full-scan.timer`:

```ini
# Toutes les 6 heures
OnCalendar=*-*-* 00,06,12,18:00:00

# Tous les lundis à 3h
OnCalendar=Mon *-*-* 03:00:00

# Tous les jours à 3h et 15h
OnCalendar=*-*-* 03,15:00:00
```

Puis:
```bash
sudo systemctl daemon-reload
sudo systemctl restart oldsites-full-scan.timer
```

### Modifier le timeout

Si le scan prend trop de temps, augmenter le timeout dans `oldsites-full-scan.service`:

```ini
# 4 heures au lieu de 2
TimeoutStartSec=14400
```

## 🔍 Dépannage

### AXFR échoue

```bash
# Tester manuellement avec dig
dig @zonedata.switch.ch ch AXFR

# Essayer un autre serveur
dig @ns1.nic.ch ch AXFR
dig @a.nic.ch ch AXFR
```

**Causes possibles:**
- ❌ Le serveur refuse les transferts AXFR (politique de sécurité)
- ❌ Firewall bloque le port 53
- ❌ Problème réseau

**Solutions:**
1. Le script essaie automatiquement plusieurs serveurs
2. Si tout échoue, il conserve l'ancien fichier `domains_ch.txt`
3. Vous pouvez créer manuellement `domains_ch.txt` avec vos domaines

### dig n'est pas installé

```bash
sudo apt install -y dnsutils
```

### Permissions

```bash
sudo chown -R www-data:www-data /opt/oldsite-scanner
sudo chmod +x /opt/oldsite-scanner/backend/fetch_ch_domains.py
```

### Le scan ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u oldsites-full-scan -n 100

# Vérifier que le fichier domains_ch.txt existe
ls -lh /opt/oldsite-scanner/domains_ch.txt

# Tester manuellement
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_ch_domains
python -m backend.scan_ch_sites --limit 10
```

## 📈 Monitoring

### Voir les statistiques

```bash
# Nombre de domaines dans le fichier
wc -l /opt/oldsite-scanner/domains_ch.txt

# Nombre de scans dans la base
sqlite3 /opt/oldsite-scanner/oldsites.db "SELECT COUNT(*) FROM scans;"

# Derniers scans
sqlite3 /opt/oldsite-scanner/oldsites.db "SELECT domain, score FROM scans s JOIN domains d ON d.id=s.domain_id ORDER BY s.scan_time DESC LIMIT 10;"
```

### Logs

```bash
# Logs de récupération des domaines
sudo journalctl -u oldsites-fetch-domains -n 50

# Logs du scan complet
sudo journalctl -u oldsites-full-scan -f

# Logs de l'API
sudo journalctl -u oldsites-api -f
```

## 🎯 Workflow complet

```
┌─────────────────────────────────────────────────────────────┐
│  Timer systemd (tous les jours à 3h00)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Récupération des domaines (fetch_ch_domains.py)        │
│     - Tente AXFR sur zonedata.switch.ch                    │
│     - Si échec: essaie ns1.nic.ch, ns2.nic.ch, etc.        │
│     - Si échec: conserve l'ancien domains_ch.txt           │
│     - Crée/met à jour domains_ch.txt                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Scan des domaines (scan_ch_sites.py)                   │
│     - Lit domains_ch.txt                                    │
│     - Scanne 1000 domaines (configurable)                  │
│     - Détecte les sites obsolètes                          │
│     - Enregistre dans oldsites.db                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Résultats disponibles                                   │
│     - Interface web: http://IP:8000                         │
│     - API: http://IP:8000/api/scans                        │
│     - Base de données: oldsites.db                         │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Recommandations

### Pour un scan complet de tous les domaines .ch

Si AXFR retourne 100'000+ domaines:

1. **Augmenter la limite progressivement:**
   ```bash
   # Jour 1: 1000 domaines
   # Jour 2: 2000 domaines
   # Jour 3: 5000 domaines
   # etc.
   ```

2. **Augmenter la concurrence:**
   Éditer `/opt/oldsite-scanner/backend/config.py`:
   ```python
   CONCURRENCY = 100  # Au lieu de 30
   ```

3. **Augmenter le timeout systemd:**
   ```ini
   TimeoutStartSec=28800  # 8 heures
   ```

4. **Surveiller les ressources:**
   ```bash
   htop
   df -h
   ```

### Pour un scan ciblé

Si vous voulez scanner seulement certains types de sites:

1. Créer un fichier personnalisé:
   ```bash
   # Filtrer seulement les domaines courts (potentiellement plus vieux)
   grep -E '^[a-z]{3,6}\.ch$' domains_ch.txt > domains_short.txt
   
   # Scanner ce fichier
   python -m backend.scan_ch_sites --domains-file domains_short.txt
   ```

## 🔒 Sécurité

- ✅ Le script tourne avec l'utilisateur `www-data` (pas root)
- ✅ Pas de données sensibles stockées
- ✅ User-Agent identifiable dans les requêtes
- ✅ Respect des timeouts pour ne pas surcharger les serveurs

## 📞 Support

En cas de problème:
1. Vérifier les logs: `sudo journalctl -u oldsites-full-scan -n 100`
2. Tester manuellement: `python -m backend.fetch_ch_domains`
3. Consulter la documentation: `README.md`
