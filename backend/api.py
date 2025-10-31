"""API FastAPI pour consulter les résultats des scans"""

import uvicorn
import os
import subprocess
import shlex
import datetime
import signal
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

# Configuration pour les jobs (fetch et scan)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # /opt/oldsite-scanner
PYTHON_BIN = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
DOMAINS_FILE = os.path.join(PROJECT_ROOT, "domains_final.txt")

# État global des jobs
JOB_STATE = {
    "state": "idle",      # idle | fetching | scanning
    "pid": None,
    "started_at": None,
    "last_exit_code": None,
    "last_job": None,
}


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


def _start_subprocess(cmd: str):
    """Lance un subprocess et retourne le process"""
    proc = subprocess.Popen(
        shlex.split(cmd),
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc


@app.post("/api/fetch/start")
async def start_fetch():
    """
    Lance la récupération des domaines .ch depuis crt.sh
    
    Returns:
        Status du job lancé
    """
    if JOB_STATE["state"] != "idle":
        return {
            "status": "busy",
            "state": JOB_STATE["state"],
            "message": f"Un job est déjà en cours: {JOB_STATE['state']}"
        }
    
    cmd = f"{PYTHON_BIN} -m backend.fetch_crtsh"
    proc = _start_subprocess(cmd)
    
    JOB_STATE.update({
        "state": "fetching",
        "pid": proc.pid,
        "started_at": datetime.datetime.utcnow().isoformat() + "Z",
        "last_job": "fetch",
        "last_exit_code": None
    })
    
    return {
        "status": "fetch_started",
        "pid": proc.pid,
        "started_at": JOB_STATE["started_at"]
    }


@app.post("/api/scan/start")
async def start_scan():
    """
    Lance le scan des domaines depuis domains_final.txt
    
    Returns:
        Status du job lancé
    """
    if JOB_STATE["state"] != "idle":
        return {
            "status": "busy",
            "state": JOB_STATE["state"],
            "message": f"Un job est déjà en cours: {JOB_STATE['state']}"
        }
    
    # Vérifier que le fichier de domaines existe
    if not os.path.exists(DOMAINS_FILE):
        return {
            "status": "error",
            "message": f"Le fichier {DOMAINS_FILE} n'existe pas. Lancez d'abord la récupération des domaines."
        }
    
    cmd = f"{PYTHON_BIN} -m backend.scan_ch_sites --domains-file {DOMAINS_FILE} --limit 800"
    proc = _start_subprocess(cmd)
    
    JOB_STATE.update({
        "state": "scanning",
        "pid": proc.pid,
        "started_at": datetime.datetime.utcnow().isoformat() + "Z",
        "last_job": "scan",
        "last_exit_code": None
    })
    
    return {
        "status": "scan_started",
        "pid": proc.pid,
        "started_at": JOB_STATE["started_at"]
    }


@app.post("/api/job/stop")
async def stop_job():
    """
    Arrête le job en cours (fetch ou scan)
    
    Returns:
        Status de l'arrêt
    """
    if JOB_STATE["state"] == "idle" or not JOB_STATE["pid"]:
        return {
            "status": "not_running",
            "message": "Aucun job en cours"
        }
    
    pid = JOB_STATE["pid"]
    job_type = JOB_STATE["state"]
    
    try:
        os.kill(pid, signal.SIGTERM)
        stopped = True
    except ProcessLookupError:
        stopped = False  # Le process était déjà mort
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de l'arrêt: {str(e)}"
        }
    
    JOB_STATE["last_exit_code"] = -1 if stopped else 0
    JOB_STATE["state"] = "idle"
    JOB_STATE["pid"] = None
    
    return {
        "status": "stopped",
        "pid": pid,
        "job_type": job_type,
        "message": f"Job {job_type} arrêté"
    }


@app.get("/api/job/status")
async def job_status():
    """
    Retourne l'état actuel des jobs
    
    Returns:
        État complet du système de jobs
    """
    # Vérifier si le process est encore vivant
    if JOB_STATE["pid"] and JOB_STATE["state"] != "idle":
        try:
            # Signal 0 ne tue pas le process, juste vérifie s'il existe
            os.kill(JOB_STATE["pid"], 0)
            # Le process existe encore
        except ProcessLookupError:
            # Le process est mort
            JOB_STATE["last_exit_code"] = 0
            JOB_STATE["state"] = "idle"
            JOB_STATE["pid"] = None
        except Exception:
            # Autre erreur (permissions, etc.)
            pass
    
    # Ajouter des infos supplémentaires
    response = dict(JOB_STATE)
    
    # Vérifier si le fichier de domaines existe
    response["domains_file_exists"] = os.path.exists(DOMAINS_FILE)
    if os.path.exists(DOMAINS_FILE):
        try:
            with open(DOMAINS_FILE, 'r') as f:
                lines = f.readlines()
                domains_count = len([l for l in lines if l.strip() and not l.startswith('#')])
                response["domains_count"] = domains_count
        except:
            response["domains_count"] = 0
    else:
        response["domains_count"] = 0
    
    return response


# Monter le répertoire frontend pour servir les fichiers statiques
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True)
