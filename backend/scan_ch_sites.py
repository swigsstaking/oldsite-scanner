"""Scanner asynchrone de sites .ch pour détecter les vieux sites"""

import asyncio
import aiohttp
import time
import re
import argparse
from backend import config, db


def score_site(headers, body_sample):
    """
    Calcule un score d'ancienneté basé sur divers critères techniques.
    Plus le score est élevé, plus le site est probablement ancien.
    """
    score = 0
    reasons = []

    # Conversion des headers en dict case-insensitive
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    # 1. Pas de HTTPS (si on a dû fallback sur HTTP)
    # Cette info sera passée par le caller
    
    # 2. Server header révélateur
    server = headers_lower.get('server', '').lower()
    if 'apache/1.' in server or 'apache/2.0' in server or 'apache/2.2' in server:
        score += 15
        reasons.append(f"Apache ancien ({server})")
    if 'iis/5' in server or 'iis/6' in server or 'iis/7' in server:
        score += 15
        reasons.append(f"IIS ancien ({server})")
    if 'php/4' in server or 'php/5.0' in server or 'php/5.1' in server or 'php/5.2' in server:
        score += 20
        reasons.append(f"PHP très ancien ({server})")
    if 'php/5.3' in server or 'php/5.4' in server or 'php/5.5' in server:
        score += 15
        reasons.append(f"PHP 5.x ancien ({server})")
    
    # 3. X-Powered-By
    powered = headers_lower.get('x-powered-by', '').lower()
    if 'php/4' in powered or 'php/5.0' in powered or 'php/5.1' in powered or 'php/5.2' in powered:
        score += 20
        reasons.append(f"X-Powered-By PHP ancien ({powered})")
    if 'php/5.3' in powered or 'php/5.4' in powered or 'php/5.5' in powered:
        score += 15
        reasons.append(f"X-Powered-By PHP 5.x ({powered})")
    if 'asp.net' in powered:
        score += 10
        reasons.append("ASP.NET classique")
    
    # 4. Content-Type avec charset ISO-8859
    content_type = headers_lower.get('content-type', '').lower()
    if 'iso-8859' in content_type or 'windows-1252' in content_type:
        score += 15
        reasons.append(f"Charset ancien ({content_type})")
    
    # 5. Analyse du body_sample
    if body_sample:
        body_lower = body_sample.lower()
        
        # HTML4 / XHTML 1.0
        if '<!doctype html public "-//w3c//dtd html 4' in body_lower:
            score += 20
            reasons.append("DOCTYPE HTML 4")
        if '<!doctype html public "-//w3c//dtd xhtml 1.0' in body_lower:
            score += 15
            reasons.append("DOCTYPE XHTML 1.0")
        
        # Meta charset ISO-8859
        if re.search(r'charset\s*=\s*["\']?iso-8859', body_lower):
            score += 15
            reasons.append("Meta charset ISO-8859")
        
        # Balises obsolètes
        obsolete_tags = ['<font', '<center', '<marquee', '<blink', '<frame']
        for tag in obsolete_tags:
            if tag in body_lower:
                score += 10
                reasons.append(f"Balise obsolète: {tag}")
                break
        
        # Styles inline excessifs (signe de vieux CMS)
        if body_lower.count('style=') > 20:
            score += 5
            reasons.append("Nombreux styles inline")
        
        # Absence de meta viewport (mobile)
        if 'viewport' not in body_lower:
            score += 5
            reasons.append("Pas de meta viewport")
        
        # Détection de vieux CMS
        if 'joomla! 1.' in body_lower or 'joomla! 2.' in body_lower:
            score += 15
            reasons.append("Joomla! ancien")
        if 'wordpress' in body_lower:
            # Recherche de version
            wp_version = re.search(r'wordpress[/\s]+(\d+\.\d+)', body_lower)
            if wp_version:
                version = float(wp_version.group(1))
                if version < 4.0:
                    score += 15
                    reasons.append(f"WordPress ancien ({version})")
        
        # Generator meta tag
        generator_match = re.search(r'<meta\s+name=["\']generator["\']\s+content=["\']([^"\']+)', body_lower)
        if generator_match:
            gen = generator_match.group(1).lower()
            if 'frontpage' in gen or 'dreamweaver' in gen or 'golive' in gen:
                score += 20
                reasons.append(f"Générateur ancien: {gen}")
    
    # 6. Absence de headers de sécurité modernes
    security_headers = ['strict-transport-security', 'x-frame-options', 'x-content-type-options', 'content-security-policy']
    missing_security = sum(1 for h in security_headers if h not in headers_lower)
    if missing_security >= 3:
        score += 10
        reasons.append(f"Manque {missing_security}/4 headers de sécurité")
    
    return score, "; ".join(reasons) if reasons else "Aucun critère d'ancienneté détecté"


async def scan_domain(session, domain, semaphore):
    """Scanne un domaine et retourne les résultats"""
    async with semaphore:
        start_time = time.time()
        
        # Essayer HTTPS d'abord, puis HTTP
        for scheme in ['https', 'http']:
            url = f"{scheme}://{domain}"
            try:
                # HEAD request pour les headers
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=config.HEAD_TIMEOUT), 
                                       allow_redirects=True) as resp:
                    headers = dict(resp.headers)
                    http_code = resp.status
                    
                    # GET partiel pour le body
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=config.PARTIAL_GET_TIMEOUT),
                                          allow_redirects=True) as resp2:
                        body_bytes = await resp2.content.read(config.SAMPLE_BYTES)
                        body_sample = body_bytes.decode('utf-8', errors='ignore')
                    
                    latency_ms = int((time.time() - start_time) * 1000)
                    
                    # Scoring
                    score, reasons = score_site(headers, body_sample)
                    
                    # Bonus si pas HTTPS
                    if scheme == 'http':
                        score += 25
                        reasons = f"Pas de HTTPS; {reasons}"
                    
                    # Sauvegarder si score suffisant
                    if score >= config.SCORE_THRESHOLD:
                        headers_str = "\n".join(f"{k}: {v}" for k, v in headers.items())
                        await db.add_scan(domain, http_code, headers_str, body_sample, score, reasons, latency_ms)
                        print(f"✓ {domain} - Score: {score} - {reasons[:80]}")
                    else:
                        print(f"○ {domain} - Score: {score} (trop faible)")
                    
                    return
                    
            except asyncio.TimeoutError:
                print(f"⏱ {domain} - Timeout")
                continue
            except aiohttp.ClientError as e:
                print(f"✗ {domain} - Erreur: {type(e).__name__}")
                continue
            except Exception as e:
                print(f"✗ {domain} - Erreur inattendue: {e}")
                continue
        
        # Si aucun schéma n'a fonctionné
        print(f"✗ {domain} - Inaccessible")


async def scan_domains_from_file(domains_file, limit=None):
    """Scanne une liste de domaines depuis un fichier"""
    # Initialiser la DB
    await db.init_db()
    
    # Lire les domaines
    try:
        with open(domains_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"❌ Fichier {domains_file} introuvable")
        return
    
    if limit:
        domains = domains[:limit]
    
    print(f"🔍 Scan de {len(domains)} domaines .ch avec concurrence={config.CONCURRENCY}")
    print(f"📊 Seuil de score: {config.SCORE_THRESHOLD}")
    print("-" * 80)
    
    # Scanner avec concurrence limitée
    semaphore = asyncio.Semaphore(config.CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=config.CONCURRENCY, limit_per_host=2)
    
    async with aiohttp.ClientSession(
        connector=connector,
        headers={'User-Agent': config.USER_AGENT}
    ) as session:
        tasks = [scan_domain(session, domain, semaphore) for domain in domains]
        await asyncio.gather(*tasks)
    
    print("-" * 80)
    print("✅ Scan terminé")


async def generate_sample_domains():
    """Génère un fichier d'exemple avec des domaines .ch"""
    sample_domains = [
        "# Fichier d'exemple de domaines .ch à scanner",
        "# Un domaine par ligne, les lignes commençant par # sont ignorées",
        "",
        "admin.ch",
        "sbb.ch",
        "cff.ch",
        "swisscom.ch",
        "post.ch",
        "srf.ch",
        "rts.ch",
        "epfl.ch",
        "ethz.ch",
        "uzh.ch",
        "unige.ch",
        "unil.ch",
        "migros.ch",
        "coop.ch",
        "manor.ch",
        "galaxus.ch",
        "digitec.ch",
        "20min.ch",
        "blick.ch",
        "tagesanzeiger.ch",
        "nzz.ch",
        "watson.ch",
    ]
    
    with open(config.DOMAINS_FILE, 'w') as f:
        f.write("\n".join(sample_domains))
    
    print(f"✅ Fichier d'exemple créé: {config.DOMAINS_FILE}")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Scanner de vieux sites .ch')
    parser.add_argument('--limit', type=int, help='Nombre maximum de domaines à scanner')
    parser.add_argument('--generate-sample', action='store_true', 
                       help='Génère un fichier d\'exemple de domaines')
    parser.add_argument('--domains-file', default=config.DOMAINS_FILE,
                       help='Fichier contenant la liste des domaines')
    
    args = parser.parse_args()
    
    if args.generate_sample:
        asyncio.run(generate_sample_domains())
    else:
        asyncio.run(scan_domains_from_file(args.domains_file, args.limit))


if __name__ == "__main__":
    main()
