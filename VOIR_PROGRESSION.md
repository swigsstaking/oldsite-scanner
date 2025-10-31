# 📊 Comment voir la progression de la récupération des domaines

## 🌐 Depuis l'interface web (NOUVEAU!)

Maintenant, la progression s'affiche **en temps réel** dans l'interface!

Quand vous cliquez sur "1. 🌐 Récupérer les domaines (.ch)", le statut affiche:

```
État: fetching (PID 12345) | 🔄 15,234 domaines trouvés...
```

Le nombre se met à jour automatiquement toutes les 5 secondes! 🎉

## 💻 Depuis le serveur

### 1. Voir les logs en temps réel

```bash
# Méthode 1: Logs du processus Python
sudo journalctl -f | grep -E "(crtsh|domaines)"

# Méthode 2: Si lancé manuellement
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_crtsh
```

Vous verrez:
```
🔍 Interrogation crt.sh pour l'année 2020...
   ✅ 2020: 15234 domaines trouvés
   📊 Progression: 15234 domaines trouvés jusqu'à présent...
🔍 Interrogation crt.sh pour l'année 2021...
   ✅ 2021: 18456 domaines trouvés
   📊 Progression: 33690 domaines trouvés jusqu'à présent...
...
```

### 2. Surveiller le fichier en temps réel

```bash
# Voir combien de domaines sont déjà dans le fichier
wc -l /opt/oldsite-scanner/domains_final.txt

# Rafraîchir toutes les 2 secondes
watch -n 2 'wc -l /opt/oldsite-scanner/domains_final.txt'
```

Sortie:
```
Every 2.0s: wc -l /opt/oldsite-scanner/domains_final.txt

45678 /opt/oldsite-scanner/domains_final.txt
```

### 3. Voir le fichier de progression

```bash
# Pendant la récupération, un fichier .progress est créé
cat /opt/oldsite-scanner/domains_final.txt.progress
```

Contenu:
```
# Récupération en cours...
# Domaines trouvés jusqu'à présent: 33690
# Dernière mise à jour: 2025-10-31 16:25:30
```

### 4. Vérifier via l'API

```bash
# Voir le statut complet
curl http://localhost:8000/api/job/status | jq

# Juste le nombre de domaines
curl -s http://localhost:8000/api/job/status | jq '.fetching_progress'
```

Réponse:
```json
{
  "state": "fetching",
  "pid": 12345,
  "started_at": "2025-10-31T15:20:00Z",
  "last_exit_code": null,
  "last_job": "fetch",
  "domains_file_exists": false,
  "domains_count": 0,
  "fetching_progress": 33690
}
```

## 📈 Comprendre la progression

### Phases de récupération

1. **Interrogation crt.sh** (2-5 minutes)
   - Requêtes parallèles pour chaque année (2020-2025)
   - Vous voyez: `🔍 Interrogation crt.sh pour l'année 2024...`
   - Progression: nombre de domaines trouvés augmente

2. **Nettoyage et déduplication** (quelques secondes)
   - Suppression des doublons
   - Nettoyage des domaines invalides
   - Vous voyez: `📊 Total brut: 125,456 domaines uniques`

3. **Sauvegarde** (quelques secondes)
   - Écriture dans `domains_final.txt`
   - Vous voyez: `💾 Sauvegarde de 125,456 domaines...`

### Temps estimés

| Nombre de domaines | Temps de récupération |
|-------------------|----------------------|
| 50,000 | ~2 minutes |
| 100,000 | ~3 minutes |
| 150,000 | ~5 minutes |

⚠️ **Note**: Le temps dépend de la vitesse de réponse de crt.sh

## 🔍 Exemples pratiques

### Surveiller depuis le serveur

```bash
# Terminal 1: Logs en temps réel
cd /opt/oldsite-scanner
source venv/bin/activate
python -m backend.fetch_crtsh

# Terminal 2: Surveiller le fichier
watch -n 2 'wc -l /opt/oldsite-scanner/domains_final.txt'

# Terminal 3: Surveiller via API
watch -n 2 'curl -s http://localhost:8000/api/job/status | jq ".fetching_progress"'
```

### Depuis votre machine locale

```bash
# Surveiller la progression via l'API
watch -n 2 'curl -s http://IP_SERVEUR:8000/api/job/status | jq ".fetching_progress"'
```

## ✅ Quand c'est terminé

Vous verrez:
- **Interface web**: `État: idle | ✅ 125,456 domaines`
- **Logs**: `✅ SUCCÈS` + statistiques
- **Fichier**: `domains_final.txt` créé avec tous les domaines

Le bouton "2. 🔍 Scanner" devient actif!

## 🐛 Dépannage

### La progression ne s'affiche pas

```bash
# Vérifier que le fichier .progress existe
ls -lh /opt/oldsite-scanner/domains_final.txt.progress

# Vérifier les permissions
sudo chown -R www-data:www-data /opt/oldsite-scanner
```

### Le nombre ne change pas

crt.sh peut être lent ou ne pas répondre. Attendez quelques minutes.

### Erreur "fetching" mais rien ne se passe

```bash
# Vérifier si le processus tourne
ps aux | grep fetch_crtsh

# Voir les logs d'erreur
sudo journalctl -u oldsites-api -n 100
```

## 💡 Astuces

### Rafraîchissement plus rapide

Modifiez le frontend pour rafraîchir plus souvent pendant la récupération:

```javascript
// Dans frontend/index.html, ligne ~719
// Rafraîchir toutes les 2 secondes au lieu de 5
setInterval(refreshJobStatus, 2000);
```

### Notification quand c'est terminé

```bash
# Script bash qui attend la fin
while true; do
    STATE=$(curl -s http://localhost:8000/api/job/status | jq -r '.state')
    if [ "$STATE" = "idle" ]; then
        echo "✅ Récupération terminée!"
        # Envoyer une notification (optionnel)
        # notify-send "Récupération terminée"
        break
    fi
    sleep 10
done
```

## 📊 Résumé

| Méthode | Temps réel | Détails | Facilité |
|---------|-----------|---------|----------|
| **Interface web** | ✅ Oui | Progression en direct | ⭐⭐⭐⭐⭐ |
| **Logs Python** | ✅ Oui | Détails complets | ⭐⭐⭐⭐ |
| **watch + wc** | ✅ Oui | Nombre de lignes | ⭐⭐⭐ |
| **API /job/status** | ✅ Oui | JSON structuré | ⭐⭐⭐⭐ |
| **Fichier .progress** | ⚠️ Manuel | Snapshot | ⭐⭐ |

**Recommandation**: Utilisez l'interface web, c'est le plus simple! 🚀
