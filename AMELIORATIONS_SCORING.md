# 🎯 Améliorations du système de scoring

## 🚀 Nouvelles fonctionnalités

L'algorithme de scoring a été **complètement amélioré** pour mieux cibler les sites **actifs MAIS obsolètes**, et filtrer les sites morts.

## 📊 Avant vs Après

### ❌ AVANT
- Détectait beaucoup de sites morts (404, 500, etc.)
- Comptait les pages parking comme "vieux sites"
- Ne distinguait pas les sites actifs des sites abandonnés
- Beaucoup de faux positifs

### ✅ APRÈS
- **Filtre automatiquement** les sites morts (score négatif)
- **Détecte et exclut** les pages parking / domaines à vendre
- **Favorise** les sites actifs avec du contenu réel
- **Pénalise** les technologies modernes (React, Vue, etc.)
- **Bonus** pour sites avec contenu structuré et images

## 🎯 Nouveau système de scoring

### Pénalités (scores négatifs = exclus)

| Critère | Score | Raison |
|---------|-------|--------|
| **HTTP 404, 500, etc.** | -100 | Site mort/inaccessible |
| **Page parking** | -80 | "Domain for sale", Sedo, etc. |
| **Page d'erreur** | -60 | "Page not found", "En construction" |
| **Contenu vide** | -50 | Moins de 100 caractères |
| **Technologies modernes** | -15 | React, Vue, Tailwind, etc. |

### Bonus (scores positifs = détecté)

| Critère | Score | Raison |
|---------|-------|--------|
| **WordPress < 3.0** | +30 | Très ancien, vulnérable |
| **Pas de HTTPS** | +25 | Site non sécurisé |
| **Joomla 1.x/2.x** | +25 | Très ancien, vulnérable |
| **PHP 4.x/5.0-5.2** | +20 | Version obsolète |
| **WordPress 3.x** | +20 | Ancien |
| **DOCTYPE HTML 4** | +20 | Standard obsolète |
| **Drupal 6/7** | +20 | Ancien |
| **Apache 1.x/2.0/2.2** | +15 | Serveur ancien |
| **Charset ISO-8859** | +15 | Encodage ancien |
| **Aucun header sécurité** | +15 | Pas de HSTS, CSP, etc. |
| **Site actif (200)** | +5 | Fonctionne |
| **Contenu structuré** | +10 | Article, section, nav, etc. |
| **Images présentes** | +5 | Site avec contenu visuel |

## 🔍 Exemples de détection

### ✅ Sites détectés (score > 40)

```
✅ old-company.ch
   Score: 75
   - Site actif (HTTP 200)
   - WordPress 3.5 (ancien)
   - Pas de HTTPS
   - Charset ISO-8859-1
   - Aucun header de sécurité moderne
   - Site avec contenu structuré (actif)
```

```
✅ museum-site.ch
   Score: 65
   - Site actif (HTTP 200)
   - DOCTYPE HTML 4
   - Apache 2.2
   - Balise obsolète: <font>
   - Pas de meta viewport
   - Site avec images (12 images)
```

### ❌ Sites exclus (score < 40)

```
❌ dead-site.ch
   Score: -100
   - Site non accessible (HTTP 404)
```

```
❌ parking-domain.ch
   Score: -80
   - Page parking / domaine à vendre
```

```
❌ modern-startup.ch
   Score: -10
   - Site actif (HTTP 200)
   - Technologie moderne détectée: react
```

```
❌ empty-site.ch
   Score: -50
   - Contenu insuffisant (site parking ou vide)
```

## 📈 Résultats attendus

### Avant l'amélioration
- 3069 domaines scannés
- ~60% de sites morts/parking
- ~40% de vrais résultats

### Après l'amélioration
- 3069 domaines scannés
- ~10-20% de sites morts/parking (filtrés)
- **~80-90% de vrais sites actifs mais obsolètes**

## 🎯 Types de sites ciblés

### ✅ Cibles idéales (score élevé)

1. **PME suisses avec vieux WordPress**
   - WordPress 3.x ou 4.x
   - Pas de HTTPS
   - Contenu actif mais technologie obsolète
   - **Potentiel de modernisation élevé**

2. **Sites institutionnels anciens**
   - HTML 4 / XHTML 1.0
   - Serveurs Apache 2.2
   - Contenu structuré mais design ancien
   - **Besoin de refonte**

3. **Sites de musées/associations**
   - Vieux CMS (Joomla 2.x, Drupal 7)
   - Contenu riche mais technologie dépassée
   - **Opportunité de modernisation**

### ❌ Sites exclus (score négatif)

1. **Sites morts**
   - HTTP 404, 500, 503
   - Aucun intérêt commercial

2. **Pages parking**
   - "Domain for sale"
   - Aucun contenu réel

3. **Sites modernes**
   - React, Vue, Next.js
   - Déjà à jour

4. **Sites vides**
   - En construction
   - Pas de contenu

## 🚀 Utilisation

### Scanner avec le nouveau système

```bash
cd /opt/oldsite-scanner
source venv/bin/activate

# Scanner 500 domaines
python -m backend.scan_ch_sites --domains-file domains_final.txt --limit 500
```

### Ajuster le seuil de score

Par défaut, le seuil est à **40 points**. Vous pouvez l'ajuster dans `backend/config.py`:

```python
# Pour être plus strict (moins de résultats, meilleure qualité)
SCORE_THRESHOLD = 60

# Pour être plus permissif (plus de résultats)
SCORE_THRESHOLD = 30
```

### Filtrer dans l'interface web

Dans l'interface, vous pouvez filtrer par score minimum:

```
Score minimum: 60  [Actualiser]
```

Cela affichera seulement les sites avec un score >= 60 (très obsolètes).

## 📊 Statistiques de qualité

### Distribution des scores attendue

| Score | Catégorie | % attendu |
|-------|-----------|-----------|
| < 0 | Sites exclus (morts/parking) | 60-70% |
| 0-39 | Sites modernes ou peu obsolètes | 10-15% |
| 40-59 | Sites obsolètes (cibles moyennes) | 10-15% |
| 60-79 | Sites très obsolètes (bonnes cibles) | 5-10% |
| 80+ | Sites extrêmement obsolètes (cibles premium) | 1-3% |

### Taux de conversion attendu

Sur 3000 domaines scannés:
- **~900-1200** sites morts/parking (exclus automatiquement)
- **~300-450** sites modernes (exclus)
- **~300-450** sites obsolètes détectés (40-59 points)
- **~150-300** sites très obsolètes (60-79 points)
- **~30-90** sites extrêmement obsolètes (80+ points)

**Total cibles intéressantes: 480-840 sites** (16-28% du total)

## 🔧 Personnalisation

### Ajouter des critères personnalisés

Éditez `backend/scan_ch_sites.py`, fonction `score_site()`:

```python
# Exemple: Détecter un vieux framework spécifique
if 'mon-vieux-framework' in body_lower:
    score += 25
    reasons.append("Mon vieux framework détecté")

# Exemple: Pénaliser un hébergeur spécifique
if 'hostinger' in headers_lower.get('server', ''):
    score -= 10
    reasons.append("Hébergeur moderne")
```

### Modifier les pénalités

```python
# Être moins strict sur les pages d'erreur
if any(keyword in body_lower for keyword in error_keywords):
    score -= 30  # Au lieu de -60
    reasons.append("Page d'erreur ou en construction")
```

## 💡 Conseils d'utilisation

### 1. Scanner par lots

```bash
# Jour 1: Scanner 500 domaines
python -m backend.scan_ch_sites --domains-file domains_final.txt --limit 500

# Analyser les résultats dans l'interface
# Ajuster le seuil si nécessaire

# Jour 2: Scanner 500 autres domaines
python -m backend.scan_ch_sites --domains-file domains_final.txt --limit 1000
```

### 2. Exporter les meilleurs résultats

```bash
# Depuis l'interface, filtrer avec score >= 60
# Ou via SQL:
sqlite3 /opt/oldsite-scanner/oldsites.db "
  SELECT d.domain, s.score, s.reasons 
  FROM scans s 
  JOIN domains d ON d.id = s.domain_id 
  WHERE s.score >= 60 
  ORDER BY s.score DESC;
"
```

### 3. Analyser les raisons

Dans l'interface, cliquez sur un domaine pour voir les détails:
- **Raisons de détection**: Pourquoi le site est considéré obsolète
- **Headers HTTP**: Technologies utilisées
- **Échantillon HTML**: Aperçu du code source

## 🎉 Résumé

L'algorithme amélioré permet de:
- ✅ **Filtrer automatiquement** 60-70% de sites non pertinents
- ✅ **Cibler précisément** les sites actifs mais obsolètes
- ✅ **Identifier** les opportunités de modernisation
- ✅ **Exclure** les faux positifs (sites morts, parking, modernes)

**Résultat: Des leads de meilleure qualité pour vos services de modernisation!** 🚀
