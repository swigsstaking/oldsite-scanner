# 📡 Documentation API

API REST pour consulter les résultats du scanner de vieux sites .ch.

## Base URL

- **Local**: `http://127.0.0.1:8000`
- **Production**: `https://scanner.votredomaine.ch`

## Authentification

Aucune authentification requise par défaut. Peut être protégé par HTTP Basic Auth (voir guide de déploiement).

## Endpoints

### 1. Liste des scans

Récupère la liste des scans avec filtres.

**Endpoint**: `GET /api/scans`

**Paramètres de requête**:

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `min_score` | integer | 0 | Score minimum pour filtrer les résultats |
| `limit` | integer | 200 | Nombre maximum de résultats à retourner |

**Exemple de requête**:

```bash
curl "http://127.0.0.1:8000/api/scans?min_score=60&limit=50"
```

**Réponse** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "domain": "example.ch",
      "scan_time": 1704067200,
      "http_code": 200,
      "score": 85,
      "reasons": "Pas de HTTPS; PHP 5.2; DOCTYPE HTML 4; Charset ISO-8859-1",
      "latency_ms": 234
    },
    {
      "id": 2,
      "domain": "oldsite.ch",
      "scan_time": 1704067150,
      "http_code": 200,
      "score": 75,
      "reasons": "Apache 2.2; PHP 5.4; Balise obsolète: <font>",
      "latency_ms": 156
    }
  ]
}
```

**Codes de statut**:
- `200 OK`: Succès
- `500 Internal Server Error`: Erreur serveur

---

### 2. Détails d'un scan

Récupère les détails complets d'un scan spécifique, incluant les headers HTTP et l'échantillon HTML.

**Endpoint**: `GET /api/scans/{scan_id}`

**Paramètres de chemin**:

| Paramètre | Type | Description |
|-----------|------|-------------|
| `scan_id` | integer | ID du scan à récupérer |

**Exemple de requête**:

```bash
curl "http://127.0.0.1:8000/api/scans/1"
```

**Réponse** (200 OK):

```json
{
  "id": 1,
  "domain": "example.ch",
  "scan_time": 1704067200,
  "http_code": 200,
  "score": 85,
  "reasons": "Pas de HTTPS; PHP 5.2; DOCTYPE HTML 4; Charset ISO-8859-1",
  "headers": "Server: Apache/2.2.22\nX-Powered-By: PHP/5.2.17\nContent-Type: text/html; charset=ISO-8859-1\nContent-Length: 5432",
  "sample_head": "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=ISO-8859-1\">\n<title>Example Site</title>\n</head>\n<body>\n<font face=\"Arial\">Welcome to our site</font>\n</body>\n</html>",
  "latency_ms": 234
}
```

**Codes de statut**:
- `200 OK`: Succès
- `404 Not Found`: Scan non trouvé
- `500 Internal Server Error`: Erreur serveur

---

### 3. Statistiques globales

Récupère des statistiques globales sur tous les scans.

**Endpoint**: `GET /api/stats`

**Paramètres**: Aucun

**Exemple de requête**:

```bash
curl "http://127.0.0.1:8000/api/stats"
```

**Réponse** (200 OK):

```json
{
  "total_scans": 156,
  "avg_score": 62.5,
  "max_score": 120,
  "domains_count": 142
}
```

**Champs de réponse**:

| Champ | Type | Description |
|-------|------|-------------|
| `total_scans` | integer | Nombre total de scans dans la base |
| `avg_score` | float | Score moyen de tous les scans |
| `max_score` | integer | Score maximum trouvé |
| `domains_count` | integer | Nombre de domaines uniques scannés |

**Codes de statut**:
- `200 OK`: Succès
- `500 Internal Server Error`: Erreur serveur

---

### 4. Page d'accueil

Sert l'interface web HTML.

**Endpoint**: `GET /`

**Réponse**: Page HTML de l'interface web

---

## Modèles de données

### Scan (liste)

```typescript
{
  id: number;              // ID unique du scan
  domain: string;          // Nom de domaine scanné
  scan_time: number;       // Timestamp Unix du scan
  http_code: number;       // Code de statut HTTP
  score: number;           // Score d'obsolescence (0-200+)
  reasons: string;         // Raisons de la détection (séparées par ;)
  latency_ms: number;      // Latence de la requête en millisecondes
}
```

### Scan (détails)

```typescript
{
  id: number;              // ID unique du scan
  domain: string;          // Nom de domaine scanné
  scan_time: number;       // Timestamp Unix du scan
  http_code: number;       // Code de statut HTTP
  score: number;           // Score d'obsolescence (0-200+)
  reasons: string;         // Raisons de la détection (séparées par ;)
  headers: string;         // Headers HTTP complets (format: "Key: Value\n...")
  sample_head: string;     // Échantillon du HTML (premiers 2048 octets)
  latency_ms: number;      // Latence de la requête en millisecondes
}
```

### Stats

```typescript
{
  total_scans: number;     // Nombre total de scans
  avg_score: number;       // Score moyen
  max_score: number;       // Score maximum
  domains_count: number;   // Nombre de domaines uniques
}
```

---

## Exemples d'utilisation

### Python

```python
import requests

# Liste des scans avec score minimum
response = requests.get(
    "http://127.0.0.1:8000/api/scans",
    params={"min_score": 70, "limit": 20}
)
scans = response.json()["items"]

for scan in scans:
    print(f"{scan['domain']}: {scan['score']} points")

# Détails d'un scan
scan_id = scans[0]["id"]
details = requests.get(f"http://127.0.0.1:8000/api/scans/{scan_id}").json()
print(details["headers"])
```

### JavaScript (fetch)

```javascript
// Liste des scans
fetch('/api/scans?min_score=60&limit=50')
  .then(response => response.json())
  .then(data => {
    data.items.forEach(scan => {
      console.log(`${scan.domain}: ${scan.score} points`);
    });
  });

// Détails d'un scan
fetch('/api/scans/1')
  .then(response => response.json())
  .then(scan => {
    console.log(scan.headers);
    console.log(scan.sample_head);
  });

// Statistiques
fetch('/api/stats')
  .then(response => response.json())
  .then(stats => {
    console.log(`Total: ${stats.total_scans} scans`);
    console.log(`Score moyen: ${stats.avg_score}`);
  });
```

### cURL

```bash
# Liste des scans
curl -X GET "http://127.0.0.1:8000/api/scans?min_score=50&limit=100" \
  -H "Accept: application/json"

# Détails d'un scan
curl -X GET "http://127.0.0.1:8000/api/scans/1" \
  -H "Accept: application/json"

# Statistiques
curl -X GET "http://127.0.0.1:8000/api/stats" \
  -H "Accept: application/json"

# Avec authentification HTTP Basic (si activée)
curl -X GET "https://scanner.votredomaine.ch/api/scans" \
  -u "username:password" \
  -H "Accept: application/json"
```

### PowerShell

```powershell
# Liste des scans
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/scans?min_score=60" -Method Get
$response.items | ForEach-Object {
    Write-Host "$($_.domain): $($_.score) points"
}

# Détails d'un scan
$scan = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/scans/1" -Method Get
Write-Host $scan.headers
```

---

## Pagination et filtrage

### Filtrage par score

Pour obtenir uniquement les sites avec un score élevé (très obsolètes):

```bash
curl "http://127.0.0.1:8000/api/scans?min_score=80&limit=50"
```

### Limitation des résultats

Pour obtenir seulement les 10 premiers résultats:

```bash
curl "http://127.0.0.1:8000/api/scans?limit=10"
```

### Combinaison de filtres

```bash
curl "http://127.0.0.1:8000/api/scans?min_score=60&limit=25"
```

---

## Gestion des erreurs

### Format des erreurs

```json
{
  "detail": "Message d'erreur"
}
```

### Codes d'erreur courants

| Code | Signification | Cause possible |
|------|---------------|----------------|
| 404 | Not Found | Scan ID inexistant |
| 422 | Unprocessable Entity | Paramètres invalides |
| 500 | Internal Server Error | Erreur base de données ou serveur |

### Exemple de gestion d'erreur (JavaScript)

```javascript
fetch('/api/scans/999999')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => console.log(data))
  .catch(error => console.error('Erreur:', error));
```

---

## Rate Limiting

Actuellement, aucune limitation de débit n'est implémentée. Pour un usage en production, il est recommandé de:

1. Configurer Nginx avec `limit_req_zone`
2. Implémenter un rate limiting dans FastAPI
3. Utiliser un reverse proxy avec rate limiting

---

## CORS

L'API autorise les requêtes CORS depuis toutes les origines en développement. En production, il est recommandé de restreindre les origines autorisées dans `backend/api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votredomaine.ch"],  # Restreindre
    allow_credentials=True,
    allow_methods=["GET"],  # Seulement GET
    allow_headers=["*"],
)
```

---

## Documentation interactive

FastAPI génère automatiquement une documentation interactive:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Ces interfaces permettent de tester l'API directement depuis le navigateur.

---

## Webhooks (à venir)

Fonctionnalité prévue pour notifier des endpoints externes lors de nouveaux scans.

---

## Support

Pour toute question sur l'API:
- Consulter la documentation interactive: `/docs`
- Ouvrir une issue sur GitHub
- Email: contact@votredomaine.ch
