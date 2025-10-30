"""API FastAPI pour consulter les résultats des scans"""

import uvicorn
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend import db

app = FastAPI(
    title="Old .ch Scanner",
    version="0.1",
    description="API pour consulter les vieux sites .ch détectés"
)

# CORS pour le développement local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


@app.on_event("startup")
async def startup():
    """Initialise la base de données au démarrage"""
    await db.init_db()


@app.get("/")
async def root():
    """Sert la page d'accueil"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/api/scans")
async def list_scans(min_score: int = 0, limit: int = 200):
    """
    Liste les scans avec un score minimum.
    
    Args:
        min_score: Score minimum pour filtrer les résultats (défaut: 0)
        limit: Nombre maximum de résultats (défaut: 200)
    
    Returns:
        Liste des scans triés par score décroissant
    """
    return {"items": await db.list_scans(limit, min_score)}


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: int):
    """
    Récupère les détails complets d'un scan spécifique.
    
    Args:
        scan_id: ID du scan
    
    Returns:
        Détails du scan incluant headers et sample HTML
    """
    item = await db.get_scan(scan_id)
    if not item:
        raise HTTPException(status_code=404, detail="Scan non trouvé")
    return item


@app.get("/api/stats")
async def get_stats():
    """Retourne des statistiques globales sur les scans"""
    # Cette fonction pourrait être étendue pour fournir plus de stats
    scans = await db.list_scans(limit=10000, min_score=0)
    
    if not scans:
        return {
            "total_scans": 0,
            "avg_score": 0,
            "max_score": 0,
            "domains_count": 0
        }
    
    scores = [s["score"] for s in scans]
    domains = set(s["domain"] for s in scans)
    
    return {
        "total_scans": len(scans),
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "domains_count": len(domains)
    }


# Monter le répertoire frontend pour servir les fichiers statiques
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True)
