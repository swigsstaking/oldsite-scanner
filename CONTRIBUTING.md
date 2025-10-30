# 🤝 Guide de contribution

Merci de votre intérêt pour contribuer à oldsite-scanner!

## 🏗️ Architecture du projet

### Backend

- **`config.py`**: Configuration globale (timeouts, concurrence, seuils)
- **`db.py`**: Couche d'accès à la base de données SQLite avec aiosqlite
- **`scan_ch_sites.py`**: Scanner asynchrone avec système de scoring
- **`api.py`**: API REST FastAPI avec endpoints pour consulter les résultats

### Frontend

- **`index.html`**: Interface web moderne en HTML/CSS/JavaScript vanilla
- Utilise l'API REST pour afficher les résultats
- Design responsive avec modal pour les détails

### Déploiement

- **`deployment/`**: Fichiers de configuration systemd, Nginx, scripts d'installation

## 🔧 Configuration de l'environnement de développement

### Prérequis

- Python 3.8+
- pip
- Git

### Installation

```bash
# Cloner le projet
git clone https://github.com/VOTRECOMPTE/oldsite-scanner.git
cd oldsite-scanner

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r backend/requirements.txt

# Installer les outils de développement
pip install black flake8 pytest pytest-asyncio
```

### Lancer les tests

```bash
# Utiliser le script de test
chmod +x test_local.sh
./test_local.sh

# Ou manuellement
python -m backend.scan_ch_sites --generate-sample
python -m backend.scan_ch_sites --limit 5
python -m backend.api
```

## 📝 Conventions de code

### Python

- Suivre PEP 8
- Utiliser `black` pour le formatage:
  ```bash
  black backend/
  ```
- Vérifier avec `flake8`:
  ```bash
  flake8 backend/ --max-line-length=100
  ```
- Docstrings pour toutes les fonctions publiques
- Type hints recommandés

### JavaScript

- Utiliser `const` et `let`, pas `var`
- Noms de variables en camelCase
- Fonctions async/await pour les appels API
- Commentaires pour la logique complexe

### Commits

Format des messages de commit:
```
type(scope): description courte

Description détaillée si nécessaire
```

Types:
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, pas de changement de code
- `refactor`: Refactoring
- `test`: Ajout de tests
- `chore`: Maintenance

Exemples:
```
feat(scanner): ajout détection WordPress ancien
fix(api): correction timeout sur /api/stats
docs(readme): mise à jour instructions déploiement
```

## 🎯 Comment contribuer

### 1. Signaler un bug

Ouvrir une issue avec:
- Description claire du problème
- Étapes pour reproduire
- Comportement attendu vs observé
- Version de Python, OS
- Logs pertinents

### 2. Proposer une fonctionnalité

Ouvrir une issue avec:
- Description de la fonctionnalité
- Cas d'usage
- Proposition d'implémentation (optionnel)

### 3. Soumettre une Pull Request

1. **Fork** le projet
2. **Créer une branche** pour votre fonctionnalité:
   ```bash
   git checkout -b feat/ma-fonctionnalite
   ```
3. **Développer** votre fonctionnalité
4. **Tester** localement:
   ```bash
   ./test_local.sh
   ```
5. **Commiter** vos changements:
   ```bash
   git commit -m "feat(scanner): ajout détection Joomla"
   ```
6. **Pousser** vers votre fork:
   ```bash
   git push origin feat/ma-fonctionnalite
   ```
7. **Ouvrir une Pull Request** sur GitHub

### Checklist PR

- [ ] Le code suit les conventions du projet
- [ ] Les tests passent localement
- [ ] La documentation est à jour
- [ ] Le commit message suit le format
- [ ] Pas de fichiers inutiles (`.pyc`, `.db`, etc.)

## 🧪 Tests

### Tests manuels

```bash
# Scanner quelques domaines
python -m backend.scan_ch_sites --limit 5

# Vérifier l'API
python -m backend.api &
curl http://127.0.0.1:8000/api/stats
curl http://127.0.0.1:8000/api/scans?limit=10
```

### Tests automatisés (à venir)

```bash
pytest tests/
```

## 💡 Idées de contributions

### Fonctionnalités

- [ ] Ajout de nouveaux critères de détection (CMS, frameworks, etc.)
- [ ] Export des résultats en CSV/JSON
- [ ] Graphiques et statistiques avancées
- [ ] Système de notifications (email, Slack, etc.)
- [ ] API pour déclencher des scans à la demande
- [ ] Support de plusieurs pays (pas seulement .ch)
- [ ] Détection de technologies modernes (React, Vue, etc.)
- [ ] Historique des scans pour suivre l'évolution

### Améliorations techniques

- [ ] Tests unitaires et d'intégration
- [ ] CI/CD avec GitHub Actions
- [ ] Support Docker
- [ ] Optimisation des performances
- [ ] Cache pour les résultats
- [ ] Rate limiting sur l'API
- [ ] Pagination améliorée

### Documentation

- [ ] Tutoriels vidéo
- [ ] Exemples d'utilisation avancée
- [ ] Guide de troubleshooting
- [ ] Documentation API (OpenAPI/Swagger)

### Frontend

- [ ] Filtres avancés (par date, par critère, etc.)
- [ ] Graphiques interactifs
- [ ] Dark mode
- [ ] Recherche en temps réel
- [ ] Export des résultats
- [ ] Comparaison de scans

## 🔍 Structure de la base de données

### Table `domains`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| domain | TEXT | Nom de domaine (unique) |
| created_at | INTEGER | Timestamp de création |

### Table `scans`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| domain_id | INTEGER | Référence vers domains.id |
| scan_time | INTEGER | Timestamp du scan |
| http_code | INTEGER | Code HTTP retourné |
| headers | TEXT | Headers HTTP complets |
| sample_head | TEXT | Échantillon du HTML |
| score | INTEGER | Score d'obsolescence |
| reasons | TEXT | Raisons de la détection |
| latency_ms | INTEGER | Latence en millisecondes |

## 📚 Ressources

### Documentation des dépendances

- [FastAPI](https://fastapi.tiangolo.com/)
- [aiohttp](https://docs.aiohttp.org/)
- [aiosqlite](https://aiosqlite.omnilib.dev/)
- [Uvicorn](https://www.uvicorn.org/)

### Standards web

- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [HTML Living Standard](https://html.spec.whatwg.org/)
- [Obsolete HTML Elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Element#obsolete_and_deprecated_elements)

## 📧 Contact

Pour toute question:
- Ouvrir une issue sur GitHub
- Email: contact@votredomaine.ch

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

Merci de contribuer à oldsite-scanner! 🎉
