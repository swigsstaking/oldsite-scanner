"""Module de gestion de la base de données SQLite"""

import aiosqlite
import time
from backend import config


async def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    async with aiosqlite.connect(config.DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS domains(
            id INTEGER PRIMARY KEY,
            domain TEXT UNIQUE,
            created_at INTEGER
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY,
            domain_id INTEGER,
            scan_time INTEGER,
            http_code INTEGER,
            headers TEXT,
            sample_head TEXT,
            score INTEGER,
            reasons TEXT,
            latency_ms INTEGER,
            FOREIGN KEY(domain_id) REFERENCES domains(id)
        );
        """)
        await db.commit()


async def add_scan(domain, http_code, headers, sample_head, score, reasons, latency_ms):
    """Ajoute un résultat de scan dans la base de données"""
    now = int(time.time())
    async with aiosqlite.connect(config.DB_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO domains(domain, created_at) VALUES (?, ?)", (domain, now))
        cur = await db.execute("SELECT id FROM domains WHERE domain=?", (domain,))
        domain_id = (await cur.fetchone())[0]
        await db.execute("""
            INSERT INTO scans(domain_id, scan_time, http_code, headers, sample_head, score, reasons, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (domain_id, now, http_code, headers, sample_head, score, reasons, latency_ms))
        await db.commit()


async def list_scans(limit=200, min_score=0):
    """Liste les scans avec un score minimum"""
    async with aiosqlite.connect(config.DB_FILE) as db:
        q = """
        SELECT s.id, d.domain, s.scan_time, s.http_code, s.score, s.reasons, s.latency_ms
        FROM scans s JOIN domains d ON d.id=s.domain_id
        WHERE s.score>=?
        ORDER BY s.score DESC, s.scan_time DESC LIMIT ?
        """
        cursor = await db.execute(q, (min_score, limit))
        rows = await cursor.fetchall()
        return [
            {"id": r[0], "domain": r[1], "scan_time": r[2], "http_code": r[3], 
             "score": r[4], "reasons": r[5], "latency_ms": r[6]}
            for r in rows
        ]


async def get_scan(scan_id: int):
    """Récupère les détails d'un scan spécifique"""
    async with aiosqlite.connect(config.DB_FILE) as db:
        q = """
        SELECT s.id, d.domain, s.scan_time, s.http_code, s.score, s.reasons, s.headers, s.sample_head, s.latency_ms
        FROM scans s JOIN domains d ON d.id=s.domain_id WHERE s.id=?
        """
        cursor = await db.execute(q, (scan_id,))
        r = await cursor.fetchone()
        if not r:
            return None
        return {
            "id": r[0], "domain": r[1], "scan_time": r[2], "http_code": r[3], 
            "score": r[4], "reasons": r[5], "headers": r[6], "sample_head": r[7], 
            "latency_ms": r[8]
        }
