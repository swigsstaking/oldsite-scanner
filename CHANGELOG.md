# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### À venir
- Tests unitaires et d'intégration
- Support Docker
- Export CSV/JSON des résultats
- Graphiques et statistiques avancées
- Support multi-pays

## [0.1.0] - 2025-01-XX

### Ajouté
- Scanner asynchrone de domaines .ch
- Système de scoring multi-critères pour détecter les sites obsolètes
- Détection de:
  - Absence de HTTPS
  - Serveurs web anciens (Apache 1.x/2.x, IIS 5/6/7)
  - PHP ancien (4.x, 5.x)
  - Encodage ISO-8859
  - DOCTYPE HTML4/XHTML 1.0
  - Balises HTML obsolètes
  - Absence de headers de sécurité
  - CMS anciens (Joomla, WordPress)
- Base de données SQLite pour stocker les résultats
- API REST FastAPI avec endpoints:
  - `GET /api/scans` - Liste des scans
  - `GET /api/scans/{id}` - Détails d'un scan
  - `GET /api/stats` - Statistiques globales
- Interface web moderne et responsive
- Modal pour afficher les détails complets
- Filtrage par score minimum
- Configuration systemd pour déploiement production
- Timer systemd pour scans automatiques
- Configuration Nginx avec support HTTPS
- Script d'installation automatique
- Documentation complète:
  - README.md avec guide d'utilisation
  - DEPLOYMENT.md avec instructions détaillées
  - CONTRIBUTING.md pour les développeurs
- Scripts de test et de lancement local

### Technique
- Python 3.8+ avec asyncio
- FastAPI pour l'API REST
- aiohttp pour les requêtes HTTP asynchrones
- aiosqlite pour la base de données
- Concurrence configurable (défaut: 30 requêtes simultanées)
- Timeouts configurables
- User-Agent personnalisable
- Déploiement sans Docker sur Ubuntu 22.04

### Documentation
- Guide d'installation locale
- Guide de déploiement serveur
- Documentation API
- Exemples d'utilisation
- Guide de contribution
- Licence MIT

## [0.0.1] - 2025-01-XX

### Ajouté
- Initialisation du projet
- Structure de base
- Configuration initiale
